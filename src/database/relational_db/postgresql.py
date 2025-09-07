import asyncio
import logging
import os
from typing import cast

from aiogram.fsm.context import FSMContext
from asyncpg import Pool, Record, create_pool

from config import BOT_CFG
from config import SQL_DB_CFG as c
from database import db
from database.sql import SQLDatabase
from helpers.pwd_mgr import EncryptedPassword

logger = logging.getLogger(__name__)


class PostgresqlManager(SQLDatabase):
    """
    Implementation of a relational database manager for PostgreSQL.
    """

    _pool: "Pool[Record]"

    async def connect(self) -> None:
        """
        Connect to PostgreSQL using DSN if available, otherwise using individual parameters.
        """
        if not hasattr(self, "_pool"):
            self._pool = await create_pool(
                dsn=c.url if c.url else None,
                host=None if c.url else c.host,
                port=None if c.url else c.port,
                user=None if c.url else c.user,
                password=None if c.url else c.password,
                database=None if c.url else c.name,
                min_size=c.min_pool_size,
                max_size=c.max_pool_size,
                max_queries=c.max_queries,
            )
            logger.info("Connected to PostgreSQL via %s", "URL" if c.url else "host/port")
            await self._create_tables()

    async def close(self) -> None:
        await self._pool.close()
        logger.info("Disconnected from PostgreSQL")

    async def create_user_if_not_exists(
        self,
        user_id: int,
        user_name: str,
        full_name: str,
        state: FSMContext,
    ) -> None:
        if await db.nosql.get_cache_user_created(state):
            return

        execute = self._execute(
            """
            INSERT INTO public.users (user_id, user_name, full_name, salt)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (user_id) DO NOTHING
            """,
            user_id,
            user_name,
            full_name,
            os.urandom(16).hex(),
        )
        set_cache = db.nosql.set_cache_user_created(state)
        await asyncio.gather(execute, set_cache)

    async def get_services(
        self,
        user_id: int,
        offset: int,
        limit: int = BOT_CFG.dynamic_buttons_limit,
    ) -> list[str]:
        records = await self._fetch_all(
            """
            SELECT service FROM(SELECT DISTINCT ON (service) service, password_id
                FROM public.passwords WHERE user_id = $1 ORDER BY service, password_id DESC)
            ORDER BY password_id DESC
            OFFSET $2 LIMIT $3
            """,
            user_id,
            offset * limit,
            limit + 1,
        )
        return [record["service"] for record in records]

    async def add_password(self, user_id: int, service: str, ciphertext: str) -> None:
        await self._execute(
            "INSERT INTO public.passwords (user_id, service, ciphertext) VALUES ($1, $2, $3)",
            user_id,
            service,
            ciphertext,
        )

    async def get_passwords_by_service(
        self,
        user_id: int,
        service: str,
        offset: int,
        limit: int = BOT_CFG.dynamic_buttons_limit,
    ) -> list[EncryptedPassword]:
        records = await self._fetch_all(
            """SELECT service, ciphertext FROM public.passwords
               WHERE user_id = $1 AND service = $2 OFFSET $3 LIMIT $4""",
            user_id,
            service,
            offset * limit,
            limit + 1,
        )
        return [
            EncryptedPassword(
                service=record["service"],
                ciphertext=record["ciphertext"],
            )
            for record in records
        ]

    async def get_rand_password(self, user_id: int) -> EncryptedPassword | None:
        record = await self._fetch_row(
            "SELECT service, ciphertext FROM public.passwords WHERE user_id = $1",
            user_id,
        )
        return (
            EncryptedPassword(
                service=record["service"],
                ciphertext=record["ciphertext"],
            )
            if record
            else None
        )

    async def change_service(self, new_service: str, user_id: int, old_service: str) -> None:
        await self._execute(
            "UPDATE public.passwords SET service = $1 WHERE user_id = $2 AND service = $3",
            new_service,
            user_id,
            old_service,
        )

    async def delete_passwords(self, user_id: int) -> None:
        await self._execute(
            "DELETE FROM public.passwords WHERE user_id = $1",
            user_id,
        )

    async def delete_passwords_by_service(self, user_id: int, service: str) -> None:
        await self._execute(
            "DELETE FROM public.passwords WHERE user_id = $1 AND service = $2",
            user_id,
            service,
        )

    async def delete_password(self, user_id: int, service: str, ciphertext: str) -> None:
        await self._execute(
            """DELETE FROM public.passwords
               WHERE user_id = $1 AND service = $2 AND ciphertext = $3""",
            user_id,
            service,
            ciphertext,
        )

    async def delete_passwords(self, user_id: int) -> None:
        await self._execute(
            "DELETE FROM public.passwords WHERE user_id = $1",
            user_id,
        )

    async def update_credentials(
        self,
        user_id: int,
        service: str,
        current_ciphertext: str,
        new_ciphertext: str,
    ) -> None:
        await self._execute(
            """UPDATE public.passwords SET ciphertext = $1
               WHERE user_id = $2 AND service = $3 AND ciphertext = $4""",
            new_ciphertext,
            user_id,
            service,
            current_ciphertext,
        )

    async def import_passwords(self, user_id: int, records: list[EncryptedPassword]) -> None:
        values = [(user_id, r.service, r.ciphertext) for r in records]

        query = """
        INSERT INTO public.passwords (user_id, service, ciphertext)
        SELECT * FROM unnest($1::int[], $2::text[], $3::text[])
        """

        await self._execute(
            query,
            [v[0] for v in values],  # user_id
            [v[1] for v in values],  # service
            [v[2] for v in values],  # ciphertext
        )

    async def export_passwords(self, user_id: int) -> list[EncryptedPassword]:
        records = await self._fetch_all(
            "SELECT service, ciphertext FROM public.passwords WHERE user_id = $1",
            user_id,
        )
        return [
            EncryptedPassword(
                service=record["service"],
                ciphertext=record["ciphertext"],
            )
            for record in records
        ]

    async def inline_search_service(
        self,
        user_id: int,
        service: str,
        limit: int = BOT_CFG.dynamic_buttons_limit,
    ) -> list[str] | None:
        records = await self._fetch_all(
            """SELECT DISTINCT service FROM public.passwords
               WHERE user_id = $1 AND service LIKE $2 LIMIT $3""",
            user_id,
            f"%{service}%",
            limit,
        )
        return [record["service"] for record in records]

    async def get_salt(self, user_id: int) -> bytes:
        result = await self._fetch_value(
            "SELECT salt FROM public.users WHERE user_id = $1",
            user_id,
        )
        salt = cast("str", result)
        return salt.encode("utf-8")

    async def _execute(self, query: str, *args: str | int | list[str] | list[int]) -> None:
        async with self._pool.acquire() as con:
            await con.execute(query, *args)

    async def _fetch_row(self, query: str, *args: str | int) -> Record | None:
        async with self._pool.acquire() as con:
            return await con.fetchrow(query, *args)

    async def _fetch_value(self, query: str, *args: str | int) -> str | int:
        async with self._pool.acquire() as con:
            return await con.fetchval(query, *args)

    async def _fetch_all(self, query: str, *args: str | int) -> list[Record]:
        async with self._pool.acquire() as con:
            return await con.fetch(query, *args)

    async def _create_tables(self) -> None:
        await self._execute(
            """
            CREATE TABLE IF NOT EXISTS public.users
            (
                user_id bigint NOT NULL PRIMARY KEY,
                user_name TEXT,
                created_at TIMESTAMP NOT NULL DEFAULT now(),
                full_name TEXT NOT NULL,
                salt TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS public.passwords
            (
                password_id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                user_id BIGINT NOT NULL REFERENCES public.users(user_id) ON DELETE CASCADE,
                service TEXT NOT NULL COLLATE "C",
                ciphertext TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_passwords_user_id_service
            ON public.passwords (user_id, service)
            """,
        )


if __name__ == "__main__":
    PostgresqlManager()
