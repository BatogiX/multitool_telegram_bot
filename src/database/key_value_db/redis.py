import asyncio
import json
import logging
from typing import Optional, Any, Union, Literal, Callable, Awaitable

from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis, ConnectionPool
from redis.typing import ExpiryT

from database.base import AbstractKeyValueDatabase
from config import key_value_db_cfg

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

    async def execute_batch(self, *coroutines: Callable[..., Awaitable[Union[str, dict[str, Any]]]], storage_key: StorageKey) -> list:
        data, commands, redis_key_data = await self._execute_pipeline(*coroutines, storage_key=storage_key)
        if redis_key_data:
            return await self._handle_storage_data(data, commands, redis_key_data)
        return data

    async def _execute_pipeline(self, *coroutines: Callable[..., Awaitable[Union[str, dict[str, Any]]]], storage_key: StorageKey):
        pipe = self.redis.pipeline()
        commands = await asyncio.gather(*[cmd(batch_mode=True) for cmd in coroutines])
        redis_key_data = None
        redis_key_state = None

        for cmd in commands:
            cmd_type = cmd.get("type")
            cmd_data = cmd.get("data")
            match cmd_type:
                case "data":  # set/get data (getting storage_data)
                    if redis_key_data:
                        continue
                    redis_key_data = self.key_builder.build(storage_key, "data")
                    await pipe.get(redis_key_data)
                case "value":
                    if isinstance(cmd_data, dict):  # set value
                        k, v = cmd_data.popitem()
                        if isinstance(v, tuple):
                            v, ex = v
                            await pipe.set(k, v, ex)
                        elif v is None:
                            await pipe.delete(k)
                        else:
                            await pipe.set(k, v)
                    elif isinstance(cmd_data, str):  # get value
                        await pipe.get(cmd_data)
                case "state":
                    redis_key_state = self.key_builder.build(storage_key, "state") if redis_key_data is None else redis_key_state
                    if cmd_data == "get":  # get state
                        await pipe.get(redis_key_state)
                    if isinstance(cmd_data, str):  # set state
                        await pipe.set(redis_key_state, cmd_data, ex=self.c.state_ttl)
                    elif cmd_data is None:  # delete state
                        await pipe.delete(redis_key_state)
        data = await pipe.execute()
        data = [d.decode() for d in data if isinstance(d, bytes)]
        return data, commands, redis_key_data

    async def _handle_storage_data(self, data: list[Optional[str]], commands: list[Union[str, dict]], redis_key_data: str) -> list:
        storage_data = {}
        idx = 0
        for d in data:
            if d[0] != "{":
                continue
            idx = data.index(d)
            data.pop(idx)
            storage_data = json.loads(d)
            break

        storage_dicts = {}
        for cmd in commands:
            cmd_type = cmd.get("type")
            if cmd_type != "data":
                continue
            cmd_data = cmd.get("data")
            if isinstance(cmd_data, dict):
                storage_dicts.update(cmd_data)
                data.insert(idx, None)
                idx += 1
            elif isinstance(cmd_data, str):
                data.insert(idx, storage_data.get(cmd_data, None))
                idx += 1
        if storage_dicts:
            storage_data.update(storage_dicts)
            await self._set_value(redis_key_data, json.dumps(storage_data))
        return data

    async def _set_value(self, key: str, value: Any, expire: Optional[ExpiryT] = None) -> None:
        await self.redis.set(key, value, ex=expire)

    async def _get_value(self, key: str) -> Optional[Any]:
        return await self.redis.get(key)

    def _create_connection_pool(self) -> ConnectionPool:
        """
        Creates a connection pool for Redis.

        :return: A Redis connection pool.
        """
        if self.c.url:
            return ConnectionPool.from_url(url=self.c.url, max_connections=self.c.max_pool_size)
        return ConnectionPool(max_connections=self.c.max_pool_size)
