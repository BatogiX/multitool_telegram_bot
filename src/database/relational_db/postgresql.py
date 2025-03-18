import logging
from typing import Optional

from asyncpg import Pool, Connection, Record, create_pool

from database.base import AbstractRelationDatabase
from helpers import PasswordManagerHelper
from config import relational_database_cfg, bot_cfg

EncryptedRecord = PasswordManagerHelper.EncryptedRecord


class PostgresqlManager(AbstractRelationDatabase):
    """
    Implementation of a relational database manager for PostgreSQL.
    """
    def __init__(self) -> None:
        self.pool: Optional[Pool] = None
        self.c = relational_database_cfg

    async def connect(self) -> None:
        """
        Connect to PostgreSQL using DSN if available, otherwise using individual parameters.
        """
        if self.pool is None:
            self.pool = await create_pool(
                dsn=self.c.url if self.c.url else None,
                host=None if self.c.url else self.c.host,
                port=None if self.c.url else self.c.port,
                user=None if self.c.url else self.c.user,
                password=None if self.c.url else self.c.password,
                database=None if self.c.url else self.c.name,
                min_size=self.c.min_pool_size,
                max_size=self.c.max_pool_size,
                max_queries=self.c.max_queries
            )
            logging.info(f"Connected to PostgreSQL via {'URL' if self.c.url else 'host/port'}")
            await self._init_db()

    async def close(self) -> None:
        await self.pool.close()
        logging.info("Disconnected from PostgreSQL")

    async def create_user_if_not_exists(self, user_id: int, user_name: str, full_name: str) -> None:
        await self._execute(
            """
            INSERT INTO public.users (user_id, user_name, full_name)
            VALUES ($1, $2, $3)
            ON CONFLICT (user_id) DO NOTHING
            """,
            user_id, user_name, full_name
        )

    async def get_services(self, user_id: int, offset: int, limit: int = bot_cfg.dynamic_buttons_limit) -> Optional[list[str]]:
        records: list[Record] = await self._fetch_all(
            "SELECT DISTINCT service FROM public.passwords WHERE user_id = $1 ORDER BY service OFFSET $2 LIMIT $3",
            user_id, offset, limit + 1
        )
        return [record.get("service") for record in records]

    async def create_password(self, user_id: int, service: str, ciphertext: str) -> None:
        await self._execute(
            "INSERT INTO public.passwords (user_id, service, ciphertext) VALUES ($1, $2, $3)",
            user_id, service, ciphertext
        )

    async def get_passwords(self, user_id: int, service: str, offset: int, limit: int) -> Optional[list[EncryptedRecord]]:
        records: list[Record] = await self._fetch_all(
            "SELECT service, ciphertext FROM public.passwords WHERE user_id = $1 AND service = $2 OFFSET $3 LIMIT $4",
            user_id, service, offset, limit + 1
        )
        return [EncryptedRecord(
            service=record.get("service"),
            ciphertext=record.get('ciphertext')
        ) for record in records]

    async def get_rand_password(self, user_id: int) -> Optional[EncryptedRecord]:
        record: Record = await self._fetch_row(
            "SELECT service, ciphertext FROM public.passwords WHERE user_id = $1",
            user_id
        )
        return EncryptedRecord(
            service=record.get("service"),
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

    async def delete_password(self, user_id: int, service: str, ciphertext: str) -> None:
        await self._execute(
            "DELETE FROM public.passwords WHERE user_id = $1 AND service = $2 AND ciphertext = $3",
            user_id, service, ciphertext
        )

    async def import_passwords(self, user_id: int, encrypted_records: list[EncryptedRecord]) -> None:
        values = [
            (user_id, r.service, r.ciphertext)
            for r in encrypted_records
        ]

        query = """
        INSERT INTO public.passwords (user_id, service, ciphertext)
        SELECT * FROM unnest($1::int[], $2::text[], $3::text[])
        """

        await self._execute(
            query,
            [v[0] for v in values],  # user_id
            [v[1] for v in values],        # service
            [v[2] for v in values]         # ciphertext
        )

    async def export_passwords(self, user_id: int) -> Optional[list[EncryptedRecord]]:
        records = await self._fetch_all(
            "SELECT service, ciphertext FROM public.passwords WHERE user_id = $1",
            user_id
        )
        return [EncryptedRecord(
            service=record.get("service"),
            ciphertext=record.get("ciphertext")
        ) for record in records]

    async def inline_search_service(self, user_id: int, service: str, limit: int) -> list[str]:
        records = await self._fetch_all(
            "SELECT DISTINCT service FROM public.passwords WHERE user_id = $1 AND service LIKE $2 LIMIT $3",
            user_id, f"%{service}%", limit
        )
        return [record.get("service") for record in records]

    async def _execute(self, query: str, *args) -> None:
        async with self.pool.acquire() as con:
            con: Connection
            await con.execute(query, *args)

    async def _fetch_row(self, query: str, *args) -> Optional[Record]:
        async with self.pool.acquire() as con:
            con: Connection
            return await con.fetchrow(query, *args)

    async def _fetch_value(self, query: str, *args) -> any:
        async with self.pool.acquire() as con:
            con: Connection
            return await con.fetchval(query, *args)

    async def _fetch_all(self, query: str, *args) -> Optional[list[Record]]:
        async with self.pool.acquire() as con:
            con: Connection
            return await con.fetch(query, *args)

    async def _init_db(self) -> None:
        await self._execute(
            '''
            CREATE TABLE IF NOT EXISTS public.users
            (
                user_id bigint NOT NULL PRIMARY KEY,
                user_name TEXT,
                created_at TIMESTAMP NOT NULL DEFAULT now(),
                full_name TEXT NOT NULL
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
            '''
        )
