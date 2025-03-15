from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base import AbstractRelationDatabase, AbstractKeyValueDatabase


class DatabaseManager:
    """
    Manages connections to both key–value and relational databases.
    Uses dependency injection for flexibility and testability.
    """
    def __init__(self, key_value_db: AbstractKeyValueDatabase, relational_db: AbstractRelationDatabase):
        self.key_value_db = key_value_db
        self.relational_db = relational_db

    async def initialize(self) -> None:
        """
        Initialize database connections.
        Connects to key–value and relational databases, and initializes the relational database.
        """
        await self.key_value_db.connect()

        await self.relational_db.connect()
        await self.relational_db.init_db()

    async def close(self) -> None:
        """
        Close all database connections.
        """
        await self.relational_db.close()
