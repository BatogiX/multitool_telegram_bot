import logging
from typing import Optional, Any

from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis, ConnectionPool
from redis.typing import ExpiryT

from config.db_config import KeyValueDatabaseConfig
from database.base import AbstractKeyValueDatabase


class RedisManager(AbstractKeyValueDatabase):
    """
    Implementation of a key–value store for Redis.
    """

    def __init__(
        self,
        state_ttl: Optional[ExpiryT] = None,
        data_ttl: Optional[ExpiryT] = None,
    ) -> None:
        self.c = KeyValueDatabaseConfig()

        self.redis = Redis(connection_pool=self._create_connection_pool(), decode_responses=True)
        self.storage = RedisStorage(redis=self.redis, state_ttl=state_ttl, data_ttl=data_ttl)

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

    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> None:
        await self.redis.set(key, value, ex=expire)

    async def get(self, key: str) -> Optional[str]:
        return await self.redis.get(key)

    def _create_connection_pool(self) -> ConnectionPool:
        """
        Creates a connection pool for Redis.

        :return: A Redis connection pool.
        """
        if self.c.url:
            return ConnectionPool.from_url(url=self.c.url, max_connections=self.c.max_pool_size)
        return ConnectionPool(max_connections=self.c.max_pool_size)
