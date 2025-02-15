import logging

import asyncpg
from asyncpg import Pool, Connection, Record

from config import bot_config as c
from db.base import AbstractRelationDatabase
from models.passwords_record import EncryptedRecord


class PostgresqlManager(AbstractRelationDatabase):
    _pool: None | Pool = None

    async def connect(self) -> Pool:
        if self._pool is None:
            if self._c.url:
                self._pool = await asyncpg.create_pool(
                    dsn=self._c.url,
                    min_size=self._c.min_pool_size,
                    max_size=self._c.max_pool_size,
                    max_queries=self._c.max_queries
                )
                logging.info("Connected to PostgreSQL via URL")
            else:
                self._pool = await asyncpg.create_pool(
                    host=self._c.host,
                    port=self._c.port,
                    user=self._c.user,
                    password=self._c.password,
                    database=self._c.name,
                    min_size=self._c.min_pool_size,
                    max_size=self._c.max_pool_size,
                    max_queries=self._c.max_queries
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

    async def _fetch_row(self, query: str, *args) -> Record | None:
        async with self._pool.acquire() as conn:
            conn: Connection
            return await conn.fetchrow(query, *args)

    async def _fetch_value(self, query: str, *args) -> any:
        async with self._pool.acquire() as conn:
            conn: Connection
            return await conn.fetchval(query, *args)

    async def _fetch_all(self, query: str, *args) -> list[Record | None]:
        async with self._pool.acquire() as conn:
            conn: Connection
            return await conn.fetch(query, *args)

    async def init_db(self) -> None:
        await self._execute(
            '''
            CREATE TABLE IF NOT EXISTS public.users
            (
                user_id bigint NOT NULL PRIMARY KEY,
                user_name text,
                created_at TIMESTAMP NOT NULL DEFAULT now(),
                full_name text NOT NULL,
                salt bytea NOT NULL
            );
            '''
        )

        await self._execute(
            '''
            CREATE TABLE IF NOT EXISTS public.passwords
            (
                user_id bigint NOT NULL,
                service text NOT NULL,
                iv bytea NOT NULL,
                tag bytea NOT NULL,
                ciphertext bytea NOT NULL,
                CONSTRAINT passwords_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users (user_id) ON DELETE CASCADE
            );
            '''
        )

    async def user_exists(self, user_id: int) -> bool:
        return await self._fetch_value(
            "SELECT EXISTS(SELECT 1 FROM public.users WHERE user_id = $1)",
            user_id
        )

    async def add_user(self, user_id: int, user_name: str, full_name: str, salt: bytes) -> None:
        await self._execute(
            "INSERT INTO public.users (user_id, user_name, full_name, salt) VALUES ($1, $2, $3, $4)",
            user_id, user_name, full_name, salt
        )

    async def get_services(self, user_id: int, offset: int, limit: int = c.dynamic_buttons_limit + 1) -> list[str]:
        records: list[Record] = await self._fetch_all(
            "SELECT DISTINCT service FROM public.passwords WHERE user_id = $1 ORDER BY service OFFSET $2 LIMIT $3",
            user_id, offset, limit
        )
        return [record.get("service") for record in records]

    async def get_salt(self, user_id: int) -> bytes:
        return await self._fetch_value(
            "SELECT salt FROM public.users WHERE user_id = $1",
            user_id
        )

    async def create_password_record(self, user_id: int, service: str, iv: bytes, tag: bytes, ciphertext: bytes) -> None:
        await self._execute(
            "INSERT INTO public.passwords (user_id, service, iv, tag, ciphertext) VALUES ($1, $2, $3, $4, $5)",
            user_id, service, iv, tag, ciphertext
        )

    async def get_passwords_records(self, user_id: int, service: str, offset: int) -> list[EncryptedRecord]:
        limit: int = c.dynamic_buttons_limit + 1
        records: list[Record] = await self._fetch_all(
            "SELECT iv, tag, ciphertext FROM public.passwords WHERE user_id = $1 AND service = $2 OFFSET $3 LIMIT $4",
            user_id, service, offset, limit
        )
        return [EncryptedRecord(
            iv=record.get("iv"),
            tag=record.get('tag'),
            ciphertext=record.get('ciphertext')
        ) for record in records]

    async def get_rand_passwords_record(self, user_id: int) -> EncryptedRecord | None:
        record: Record = await self._fetch_row(
            "SELECT iv, tag, ciphertext FROM public.passwords WHERE user_id = $1",
            user_id
        )
        return EncryptedRecord(
            iv=record.get("iv"),
            tag=record.get('tag'),
            ciphertext=record.get('ciphertext')
        ) if record else None

    async def change_service(self, new_service: str, user_id: int, old_service: str) -> None:
        await self._execute(
            "UPDATE public.passwords SET service = $1 WHERE user_id = $2 AND service = $3",
            new_service, user_id, old_service
        )

    async def delete_services(self, user_id: int) -> None:
        await self._execute(
            "DELETE FROM public.passwords WHERE user_id = $1",
            user_id
        )

    async def delete_service(self, user_id: int, service: str) -> None:
        await self._execute(
            "DELETE FROM public.passwords WHERE user_id = $1 AND service = $2",
            user_id, service
        )

    async def delete_passwords_record(self, user_id: int, service: str, ciphertext: bytes) -> None:
        await self._execute(
            "DELETE FROM public.passwords WHERE user_id = $1 AND service = $2 AND ciphertext = $3",
            user_id, service, ciphertext
        )
