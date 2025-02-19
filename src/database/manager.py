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
        if self.key_value_db:
            await self.key_value_db.connect()
        if self.relational_db:
            await self.relational_db.connect()
            await self.relational_db.init_db()

    async def close(self) -> None:
        """
        Close all database connections.
        """
        if self.key_value_db:
            await self.key_value_db.disconnect()
        if self.relational_db:
            await self.relational_db.disconnect()
