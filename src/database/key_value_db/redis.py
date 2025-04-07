import logging
from typing import Optional, Any, Literal, Coroutine, Union

from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis, ConnectionPool

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
        storage_data_key: str = ""
        actions = [self._parse_coroutine(coro) for coro in coroutines]

        for action in actions:
            if action.type == BaseDataAction.type:          # set/get data (getting storage_data)
                if storage_data_key:
                    continue
                action: Union[SetDataAction, GetFromDataAction]
                storage_data_key = action.data.key
                await pipe.get(storage_data_key)
            elif action.type == BaseValueAction.type:
                if action.action == SetAction.action:       # set
                    action: SetAction
                    await pipe.set(action.data.key, action.data.value, action.data.expire)

                elif action.action == GetAction.action:     # get
                    action: GetAction
                    await pipe.get(action.data.key)

                elif action.action == DeleteAction.action:  # delete
                    action: DeleteAction
                    await pipe.delete(action.data.key)

        data = await pipe.execute()
        for idx, item in enumerate(data):
            if isinstance(item, bytes):
                data[idx] = item.decode()
        return data, actions, storage_data_key

    async def _set(self, obj: BaseKeyValueSet) -> None:
        await self.redis.set(name=obj.key, value=obj.value, ex=obj.expire)

    async def _get(self, obj: BaseKeyValueGet) -> Optional[Any]:
        return await self.redis.get(obj.key)

    async def _delete(self, obj: BaseKeyValueGet):
        await self.redis.delete(obj.key)

    def _create_connection_pool(self) -> ConnectionPool:
        """
        Creates a connection pool for Redis.

        :return: A Redis connection pool.
        """
        if self.c.url:
            return ConnectionPool.from_url(url=self.c.url, max_connections=self.c.max_pool_size)
        return ConnectionPool(max_connections=self.c.max_pool_size)
