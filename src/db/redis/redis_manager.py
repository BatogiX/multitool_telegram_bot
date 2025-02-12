import logging

from redis.asyncio import Redis

from db.base import AbstractKeyValueDatabase


class RedisManager(AbstractKeyValueDatabase):
    _pool: None | Redis = None

    async def connect(self) -> Redis:
        if not self._pool:
            if self._c.url:
                self._pool = Redis.from_url(
                    url=self._c.url,
                    max_connections=self._c.max_pool_size,
                    decode_responses=True,
                )
                await self._pool.ping()
                logging.info("Connected to Redis via URL")
            else:
                self._pool = Redis(
                    host=self._c.host,
                    port=self._c.port,
                    username=self._c.username,
                    password=self._c.password,
                    max_connections=self._c.max_pool_size,
                    decode_responses=True,
                )
                await self._pool.ping()
                logging.info("Connected to Redis")
        return self._pool

    async def disconnect(self) -> None:
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
