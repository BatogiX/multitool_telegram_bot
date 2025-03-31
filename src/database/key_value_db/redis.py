import logging
from typing import Optional, Any

from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis, ConnectionPool
import json

from database.base import AbstractKeyValueDatabase
from config import key_value_db_cfg


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

    async def get_values(self, *keys: str, state: FSMContext) -> list[Any]:
        pipe = self.redis.pipeline(transaction=False)

        data_retrieved = False
        for key in keys:
            if key.endswith("_data"):
                if data_retrieved:
                    continue
                data_retrieved = True
                data_redis_key = self.key_builder.build(state.key, "data")
                await pipe.get(data_redis_key)
            elif key == "state":
                state_redis_key = self.key_builder.build(state.key, "state")
                await pipe.get(state_redis_key)
            else:
                await pipe.get(key)
        data = await pipe.execute()

        answers = []
        storage_data = dict()
        data_retrieved = False
        for key in keys:
            if key.endswith("_data"):
                if data_retrieved:
                    answers.append(storage_data[key])
                    continue
                data_retrieved = True
                storage_data = json.loads(data.pop(0))
                answers.append(storage_data[key])
            else:
                answers.append(data.pop(0))
        print(storage_data)
        print(keys)
        print(answers)
        return answers


    async def close(self) -> None:
        await self.redis.close()
        logging.info("Disconnected from Redis")

    async def _set(self, data: dict[str, Any], expire: Optional[int] = None) -> None:
        key, value = next(iter(data.items()))
        await self.redis.set(key, value, ex=expire)

    async def _get(self, key: str) -> Optional[Any]:
        return await self.redis.get(key)

    def _create_connection_pool(self) -> ConnectionPool:
        """
        Creates a connection pool for Redis.

        :return: A Redis connection pool.
        """
        if self.c.url:
            return ConnectionPool.from_url(url=self.c.url, max_connections=self.c.max_pool_size)
        return ConnectionPool(max_connections=self.c.max_pool_size)
