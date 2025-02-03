from .base import AbstractRelationDatabase, AbstractKeyValueDatabase


class DatabaseManager:
    def __init__(
        self,
        key_value_db: AbstractKeyValueDatabase = None,
        relation_db: AbstractRelationDatabase = None
    ):
        self.key_value_db = key_value_db
        self.relation_db = relation_db

    async def connect(self):
        """Connect all databases."""
        if self.key_value_db:
            await self.key_value_db.connect()
        if self.relation_db:
            await self.relation_db.connect()

    async def disconnect(self):
        """Disconnect all databases."""
        if self.key_value_db:
            await self.key_value_db.disconnect()
        if self.relation_db:
            await self.relation_db.disconnect()
