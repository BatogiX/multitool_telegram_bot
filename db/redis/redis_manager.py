import logging

from redis.asyncio import Redis

from config import REDIS_HOST_ENV_VAR, REDIS_PORT_ENV_VAR, REDIS_USERNAME_ENV_VAR, REDIS_PASSWORD_ENV_VAR


class RedisManager:
    connection: None | Redis = None

    @classmethod
    async def connect(cls) -> Redis:
        if not cls.connection:
            cls.connection = Redis(
                host=REDIS_HOST_ENV_VAR,
                port=REDIS_PORT_ENV_VAR,
                decode_responses=True,
                username=REDIS_USERNAME_ENV_VAR,
                password=REDIS_PASSWORD_ENV_VAR,
            )
            logging.info("Connected to Redis")
        return cls.connection

    @classmethod
    async def disconnect(cls) -> None:
        if cls.connection:
            await cls.connection.close()
            logging.info("Disconnected from Redis")
            cls.connection = None
