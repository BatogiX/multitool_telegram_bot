from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .nosql import NoSQLDatabase
    from .sql import SQLDatabase


class DatabaseManager:
    """
    Manages connections to both key-value and relational databases.
    Uses dependency injection for flexibility and testability.
    """

    nosql: NoSQLDatabase
    sql: SQLDatabase

    async def initialize(self) -> None:
        """
        Initialize database connections.
        Connects to key-value and relational databases, and initializes the relational database.
        """
        self.nosql = self._create_nosql_instance()
        self.sql = self._create_sql_instance()

        await asyncio.gather(
            self.nosql.connect(),
            self.sql.connect(),
        )

    async def close(self) -> None:
        """
        Close all database connections.
        """
        await asyncio.gather(
            self.nosql.close(),
            self.sql.close(),
        )

    @staticmethod
    def _create_nosql_instance() -> NoSQLDatabase:
        from .nosql import NoSQLDatabase  # noqa: PLC0415

        return NoSQLDatabase()

    @staticmethod
    def _create_sql_instance() -> SQLDatabase:
        from .sql import SQLDatabase  # noqa: PLC0415

        return SQLDatabase()


db = DatabaseManager()
