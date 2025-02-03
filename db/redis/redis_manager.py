import logging

from redis.asyncio import Redis

from config import config
from db.base import AbstractKeyValueDatabase


class RedisManager(AbstractKeyValueDatabase):
    _pool: None | Redis = None

    @classmethod
    async def connect(cls) -> Redis:
        if not cls._pool:
            cls._pool = Redis(
                host=config.REDIS_HOST_ENV_VAR,
                port=config.REDIS_PORT_ENV_VAR,
                username=config.REDIS_USERNAME_ENV_VAR,
                password=config.REDIS_PASSWORD_ENV_VAR,
                max_connections=config.KEY_VALUE_DB_MAX_POOL_SIZE,
                decode_responses=True,
            )
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