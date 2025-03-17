from typing import Type, Union, cast

from .base import AbstractRelationDatabase, AbstractKeyValueDatabase

DatabaseType = Union[AbstractKeyValueDatabase, AbstractRelationDatabase]


class DatabaseManager:
    """
    Manages connections to both key–value and relational databases.
    Uses dependency injection for flexibility and testability.
    """
    def __init__(self, key_value_db_backend: str, relational_db_backend: str):
        self._key_value_db_backend = key_value_db_backend
        self._relational_db_backend = relational_db_backend

        self.key_value_db: AbstractKeyValueDatabase = cast(AbstractKeyValueDatabase, None)  # Will be initialized in `initialize()`
        self.relational_db: AbstractRelationDatabase = cast(AbstractRelationDatabase, None)  # Will be initialized in `initialize()`

    async def initialize(self) -> None:
        """
        Initialize database connections.
        Connects to key–value and relational databases, and initializes the relational database.
        """
        self.key_value_db = self._create_instance(self._key_value_db_backend)
        self.relational_db = self._create_instance(self._relational_db_backend)

        await self.key_value_db.connect()
        await self.relational_db.connect()

    async def close(self) -> None:
        """
        Close all database connections.
        """
        await self.key_value_db.close()
        await self.relational_db.close()

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
