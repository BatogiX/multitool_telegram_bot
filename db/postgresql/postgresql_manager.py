import logging

import asyncpg
from asyncpg import Pool, Connection

from config import relational_db_config as rdc, connection_pool_config as cpc
from db.base import AbstractRelationDatabase


class PostgresqlManager(AbstractRelationDatabase):
    _pool: None | Pool = None

    async def connect(self) -> Pool:
        if self._pool is None:
            if rdc.PG_DB_URL:
                self._pool = await asyncpg.create_pool(
                    dsn=rdc.url,
                    min_size=cpc.relational_min_pool_size,
                    max_size=cpc.relational_max_pool_size,
                    max_queries=cpc.relational_max_queries
                )
            else:
                self._pool = await asyncpg.create_pool(
                    host=rdc.host,
                    port=rdc.port,
                    user=rdc.user,
                    password=rdc.password,
                    database=rdc.name,
                    min_size=cpc.relational_min_pool_size,
                    max_size=cpc.relational_max_pool_size,
                    max_queries=cpc.relational_max_queries
                )
            logging.info("Connected to PostgreSQL")
        return self._pool

    async def disconnect(self) -> None:
        if self._pool:
            await self._pool.close()
            logging.info("Disconnected from PostgreSQL")
            self._pool = None

    async def _execute(self, query: str, *args) -> None:
        async with self._pool.acquire() as conn:
            conn: Connection
            await conn.execute(query, *args)

    async def _fetch_one(self, query: str, *args) -> any:
        async with self._pool.acquire() as conn:
            conn: Connection
            return await conn.fetchrow(query, *args)

    async def _fetch_all(self, query: str, *args) -> any:
        async with self._pool.acquire() as conn:
            conn: Connection
            return await conn.fetch(query, *args)

    async def init_db(self) -> None:
        await self._execute(
            '''
            CREATE TABLE IF NOT EXISTS public.users
            (
                user_id bigint NOT NULL,
                user_name text NOT NULL,
                created_at timestamp without time zone NOT NULL DEFAULT now(),
                full_name text NOT NULL,
                CONSTRAINT users_pkey PRIMARY KEY (user_id)
            )
            '''
        )

    async def user_exists(self, user_id: int) -> bool:
        return await self._fetch_one(
            "SELECT EXISTS(SELECT 1 FROM public.users WHERE user_id = $1)", user_id
        )

    async def add_user(self, user_id: int, user_name: str, full_name: str) -> None:
        await self._execute(
            "INSERT INTO public.users (user_id, user_name, full_name) VALUES ($1, $2, $3)", user_id, user_name, full_name
        )
