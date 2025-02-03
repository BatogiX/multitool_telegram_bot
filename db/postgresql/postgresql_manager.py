import logging

import asyncpg
from asyncpg import Pool, Connection

import config as c
from db.base import AbstractRelationDatabase


class PostgresqlManager(AbstractRelationDatabase):
    _pool: None | Pool = None

    @classmethod
    async def connect(cls) -> Pool:
        if cls._pool is None:
            if c.PG_DB_URL:
                cls._pool = await asyncpg.create_pool(
                    dsn=c.RELATIONAL_DB_URL,
                    min_size=c.RELATIONAL_DB_MIN_POOL_SIZE,
                    max_size=c.RELATIONAL_DB_MAX_POOL_SIZE,
                    max_queries=c.RELATIONAL_DB_MAX_QUERIES
                )
            else:
                cls._pool = await asyncpg.create_pool(
                    host=c.RELATIONAL_DB_HOST,
                    port=c.RELATIONAL_DB_PORT,
                    user=c.RELATIONAL_DB_USER,
                    password=c.RELATIONAL_DB_PASSWORD,
                    database=c.RELATIONAL_DB_NAME,
                    min_size=c.RELATIONAL_DB_MIN_POOL_SIZE,
                    max_size=c.RELATIONAL_DB_MAX_POOL_SIZE,
                    max_queries=c.RELATIONAL_DB_MAX_QUERIES
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