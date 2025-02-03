import logging

import asyncpg
from asyncpg import Pool, Connection

import config
from db.base import AbstractRelationDatabase


class PostgresqlManager(AbstractRelationDatabase):
    _pool: None | Pool = None

    @classmethod
    async def connect(cls) -> Pool:
        if cls._pool is None:
            if config.POSTGRESQL_URI_ENV_VAR:
                cls._pool = await asyncpg.create_pool(
                    dsn=config.POSTGRESQL_URI_ENV_VAR,
                    min_size=config.RELATION_DB_MIN_POOL_SIZE,
                    max_size=config.RELATION_DB_MAX_POOL_SIZE,
                    max_queries=config.RELATION_DB_MAX_QUERIES
                )
            else:
                cls._pool = await asyncpg.create_pool(
                    host=config.POSTGRESQL_HOST_ENV_VAR,
                    port=config.POSTGRESQL_PORT_ENV_VAR,
                    user=config.POSTGRESQL_USER_ENV_VAR,
                    password=config.POSTGRESQL_PASSWORD_ENV_VAR,
                    database=config.POSTGRESQL_DATABASE_ENV_VAR,
                    min_size=config.RELATION_DB_MIN_POOL_SIZE,
                    max_size=config.RELATION_DB_MAX_POOL_SIZE,
                    max_queries=config.RELATION_DB_MAX_QUERIES
                )
            logging.info("Connected to PostgreSQL")
        return cls._pool

    @classmethod
    async def disconnect(cls) -> None:
        if cls._pool:
            await cls._pool.close()
            logging.info("Disconnected from PostgreSQL")
            cls._pool = None

    async def execute(self, query: str, *args):
        async with self._pool.acquire() as conn:
            conn: Connection
            await conn.execute(query, *args)

    async def fetch_one(self, query: str, *args):
        async with self._pool.acquire() as conn:
            conn: Connection
            return await conn.fetchrow(query, *args)

    async def fetch_all(self, query: str, *args):
        async with self._pool.acquire() as conn:
            conn: Connection
            return await conn.fetch(query, *args)