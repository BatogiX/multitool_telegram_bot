from __future__ import annotations

import asyncio
from typing import Type, Union, TYPE_CHECKING

from config import key_value_db_cfg, relational_db_cfg

if TYPE_CHECKING:
    from .base import AbstractRelationDatabase, AbstractKeyValueDatabase
    DatabaseType = Union[AbstractKeyValueDatabase, AbstractRelationDatabase]


class DatabaseManager:
    """
    Manages connections to both key–value and relational databases.
    Uses dependency injection for flexibility and testability.
    """
    key_value_db: AbstractKeyValueDatabase
    relational_db: AbstractRelationDatabase

    async def initialize(self) -> None:
        """
        Initialize database connections.
        Connects to key–value and relational databases, and initializes the relational database.
        """
        self.key_value_db = self._create_instance(key_value_db_cfg.backend)
        self.relational_db = self._create_instance(relational_db_cfg.backend)

        await asyncio.gather(
            self.key_value_db.connect(),
            self.relational_db.connect()
        )

    async def close(self) -> None:
        """
        Close all database connections.
        """
        await asyncio.gather(
            self.key_value_db.close(),
            self.relational_db.close()
        )

    @classmethod
    def _create_instance(cls, db_name: str) -> DatabaseType:
        backend_cls = cls._resolve_backend_types(db_name)
        return backend_cls()

    @classmethod
    def _resolve_backend_types(cls, db_name: str) -> Type[DatabaseType]:
        from database.relational_db import PostgresqlManager
        from database.key_value_db import RedisManager, MemoryStorageManager

        BACKEND_MAPPING = {
            "redis": RedisManager,
            "memory": MemoryStorageManager,
            "postgres": PostgresqlManager,
        }
        return BACKEND_MAPPING[db_name]


db_manager: DatabaseManager = DatabaseManager()
