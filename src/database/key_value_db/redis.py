import logging
from typing import Optional, Any, Literal, Coroutine

from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis, ConnectionPool
from redis.typing import ExpiryT

from database.base import AbstractKeyValueDatabase
from config import key_value_db_cfg
from models.kv import *

type_of_kv = Literal["data", "value", "state"]


class RedisManager(AbstractKeyValueDatabase):
    """
    Implementation of a key–value store for Redis.
    """
    def __init__(self) -> None:
        self.c = key_value_db_cfg
        self.redis = Redis(connection_pool=self._create_connection_pool(), decode_responses=True)
        self.storage = RedisStorage(redis=self.redis, state_ttl=self.c.state_ttl, data_ttl=self.c.data_ttl)

    async def connect(self) -> None:
        try:
            await self.redis.ping()
        except Exception as e:
            logging.error(f"Failed to connect to Redis: {e}")
        else:
            logging.info(f"Connected to Redis via {'URL' if self.c.url else 'host/port'}")

    async def close(self) -> None:
        await self.redis.close()
        logging.info("Disconnected from Redis")

    async def execute_batch(self, *coroutines: Coroutine) -> tuple[Any, ...]:
        data, commands, redis_key_data = await self._execute_pipeline(*coroutines)
        if redis_key_data:
            return await self._handle_storage_data(data, commands, redis_key_data)
        return tuple(data)

    async def _execute_pipeline(self, *coroutines: Coroutine):
        pipe = self.redis.pipeline()
        redis_key_data: str = ""
        commands = [self._parse_coroutine(coro) for coro in coroutines]

        for cmd in commands:
            if cmd.type == BaseDataAction.type:                    # set/get data (getting storage_data)
                if redis_key_data:
                    continue
                redis_key_data = self.key_builder.build(cmd.storage_key, "data")
                await pipe.get(redis_key_data)
            elif cmd.type == BaseValueAction.type:
                if cmd.action == SetAction.action:       # set value
                    k, v = cmd.data.popitem()                 # noqa
                    if isinstance(v, tuple):                  # setting value with expiration
                        v, ex = v
                        await pipe.set(k, v, ex)
                    else:                                     # setting value without expiration
                        await pipe.set(k, v)
                elif cmd.action == GetAction.action:     # get value
                    await pipe.get(cmd.data)                  # noqa
                elif cmd.action == DeleteAction.action:  # delete state
                    await pipe.delete(cmd.data)

        data = await pipe.execute()
        for idx, item in enumerate(data):
            if isinstance(item, bytes):
                data[idx] = item.decode()
        return data, commands, redis_key_data

    async def _set(self, key: str, value: Any, expire: Optional[ExpiryT] = None) -> None:
        await self.redis.set(key, value, ex=expire)

    async def _get(self, key: str) -> Optional[Any]:
        return await self.redis.get(key)

    async def _delete(self, key: str):
        await self.redis.delete(key)

    def _create_connection_pool(self) -> ConnectionPool:
        """
        Creates a connection pool for Redis.

        :return: A Redis connection pool.
        """
        if self.c.url:
            return ConnectionPool.from_url(url=self.c.url, max_connections=self.c.max_pool_size)
        return ConnectionPool(max_connections=self.c.max_pool_size)
