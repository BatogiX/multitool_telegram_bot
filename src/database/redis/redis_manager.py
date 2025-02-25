import logging

from redis.asyncio import Redis

from database.base import AbstractKeyValueDatabase


class RedisManager(AbstractKeyValueDatabase):
    """
    Implementation of a key–value store for Redis.
    """
    _pool: Redis | None = None

    async def connect(self) -> Redis:
        """
        Connect to Redis using URL if provided, otherwise use host and port.
        """
        if self._pool is None:
            self._pool = Redis.from_url(
                url=self._c.url,
                max_connections=self._c.max_pool_size,
                decode_responses=True,
            ) if self._c.url else Redis(
                host=self._c.host,
                port=self._c.port,
                username=self._c.username,
                password=self._c.password,
                max_connections=self._c.max_pool_size,
                decode_responses=True,
            )
            await self._pool.ping()
            logging.info(f"Connected to Redis via {'URL' if self._c.url else 'host/port'}")
        return self._pool

    async def disconnect(self) -> None:
        """
        Disconnect from Redis.
        """
        if self._pool:
            await self._pool.close()
            logging.info("Disconnected from Redis")
            self._pool = None

    async def get(self, key: str):
        return await self._pool.get(key)

    async def set(self, key: str, value: str, expire: int = None):
        await self._pool.set(key, value, ex=expire)

    async def delete(self, key: str):
        await self._pool.delete(key)
