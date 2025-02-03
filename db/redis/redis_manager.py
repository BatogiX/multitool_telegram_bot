import logging

from redis.asyncio import Redis

import config as c
from db.base import AbstractKeyValueDatabase


class RedisManager(AbstractKeyValueDatabase):
    _pool: None | Redis = None

    @classmethod
    async def connect(cls) -> Redis:
        if not cls._pool:
            if c.REDIS_DB_URL:
                cls._pool = Redis.from_url(
                url=c.REDIS_DB_URL,
                max_connections=c.KEY_VALUE_DB_MAX_POOL_SIZE,
                decode_responses=True,
                )
            else:
                cls._pool = Redis(
                    host=c.KEY_VALUE_DB_HOST,
                    port=c.KEY_VALUE_DB_PORT,
                    username=c.KEY_VALUE_DB_USERNAME,
                    password=c.KEY_VALUE_DB_PASSWORD,
                    max_connections=c.KEY_VALUE_DB_MAX_POOL_SIZE,
                    decode_responses=True,
                )
            await cls._pool.ping()
            logging.info("Connected to Redis")
        return cls._pool

    @classmethod
    async def disconnect(cls) -> None:
        if cls._pool:
            await cls._pool.close()
            logging.info("Disconnected from Redis")
            cls._pool = None

    async def get(self, key: str):
        return await self._pool.get(key)

    async def set(self, key: str, value: str, expire: int = None):
        await self._pool.set(key, value, ex=expire)

    async def delete(self, key: str):
        await self._pool.delete(key)