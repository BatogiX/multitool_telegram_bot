import logging

from redis.asyncio import Redis

from db.base import AbstractKeyValueDatabase


class RedisManager(AbstractKeyValueDatabase):
    _pool: None | Redis = None

    @classmethod
    async def connect(cls) -> Redis:
        if not cls._pool:
            from config import key_value_db_config as kdc, connection_pool_config as cpc

            if kdc.url:
                cls._pool = Redis.from_url(
                url=kdc.url,
                max_connections=cpc.key_value_max_pool_size,
                decode_responses=True,
                )
            else:
                cls._pool = Redis(
                    host=kdc.host,
                    port=kdc.port,
                    username=kdc.username,
                    password=kdc.password,
                    max_connections=cpc.key_value_max_pool_size,
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