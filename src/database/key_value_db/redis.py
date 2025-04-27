import logging
from typing import Optional, Any, Coroutine, Union, override

from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis, ConnectionPool

from config import key_value_db_cfg
from database.base import AbstractKeyValueDatabase
from models.actions import (
    SetDataAction, SetAction, GetFromDataAction, GetAction, DeleteAction, BaseDataAction,
    BaseValueAction
)


class RedisManager(AbstractKeyValueDatabase):
    """
    Implementation of a key–value store for Redis.
    """

    def __init__(self) -> None:
        self.c = key_value_db_cfg
        self.redis = Redis(connection_pool=self._create_connection_pool(), decode_responses=True)
        self.storage = RedisStorage(
            redis=self.redis, state_ttl=self.c.state_ttl, data_ttl=self.c.data_ttl
        )

    @override
    async def connect(self) -> None:
        try:
            await self.redis.ping()
        except Exception as e:
            logging.error(f"Failed to connect to Redis: {e}")
        else:
            logging.info(f"Connected to Redis via {'URL' if self.c.url else 'host/port'}")

    @override
    async def close(self) -> None:
        await self.redis.close()
        logging.info("Disconnected from Redis")

    @override
    async def execute_batch[T](self, *coroutines: Coroutine[Any, Any, T]) -> tuple[T, ...]:
        data, commands, storage_key = await self._execute_pipeline(*coroutines)
        if storage_key:
            return await self._handle_storage_data(data, commands, storage_key)
        return tuple(data)

    async def _execute_pipeline(
        self, *coroutines: Coroutine
    ) -> tuple[list, list[Union[SetDataAction, GetFromDataAction]], Optional[StorageKey]]:
        pipe = self.redis.pipeline()
        storage_key: Optional[StorageKey] = None
        actions = [self._parse_coroutine(coro) for coro in coroutines]

        for action in actions:
            if action.type == BaseDataAction.type:  # set/get data (getting storage_data)
                if storage_key:
                    continue
                action: Union[SetDataAction, GetFromDataAction]
                storage_key = action.data.storage_key
                pipe = pipe.get(action.data.key_builder.build(storage_key, "data"))
            elif action.type == BaseValueAction.type:
                if action.action == SetAction.action:  # set
                    action: SetAction
                    pipe = pipe.set(action.data.key, action.data.value, action.data.expire)

                elif action.action == GetAction.action:  # get
                    action: GetAction
                    pipe = pipe.get(action.data.key)

                elif action.action == DeleteAction.action:  # delete
                    action: DeleteAction
                    pipe = pipe.delete(action.data.key)

        data = await pipe.execute()
        for idx, item in enumerate(data):
            if isinstance(item, bytes):
                item = item.decode()
            elif isinstance(item, bool):
                item = str(item)
            data[idx] = item

        actions = [action for action in actions if action.type == BaseDataAction.type]
        return data, actions, storage_key

    @override
    async def _set(self, obj):
        await self.redis.set(name=obj.key, value=obj.value, ex=obj.expire)

    @override
    async def _get(self, obj):
        return await self.redis.get(obj.key)

    @override
    async def _delete(self, obj):
        await self.redis.delete(obj.key)

    def _create_connection_pool(self) -> ConnectionPool:
        """
        Creates a connection pool for Redis.

        :return: A Redis connection pool.
        """
        if self.c.url:
            return ConnectionPool.from_url(url=self.c.url, max_connections=self.c.max_pool_size)
        return ConnectionPool(max_connections=self.c.max_pool_size)
