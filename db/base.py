from abc import ABC, abstractmethod


class AbstractDatabase(ABC):
    """Base abstract class for all DBs."""

    @abstractmethod
    async def connect(self):
        """Method for establishing a connection to the database."""
        pass

    @abstractmethod
    async def disconnect(self):
        """Method for closing a connection."""
        pass


class AbstractKeyValueDatabase(AbstractDatabase):
    """Abstract class for key-value storage (Redis, Memcached)."""

    @abstractmethod
    async def get(self, key: str):
        """Get value by key."""
        pass

    @abstractmethod
    async def set(self, key: str, value: str, expire: int = None):
        """Set a value by key with expiration option."""
        pass

    @abstractmethod
    async def delete(self, key: str):
        """Delete key from storage."""
        pass


class AbstractRelationDatabase(AbstractDatabase):
    """Abstract class for relational databases."""

    @abstractmethod
    async def execute(self, query: str, *args):
        """Execute an SQL query without returning a result (INSERT, UPDATE, DELETE)."""
        pass

    @abstractmethod
    async def fetch_one(self, query: str, *args):
        """Get one record from the database."""
        pass

    @abstractmethod
    async def fetch_all(self, query: str, *args):
        """Get a list of records from the database."""
        pass
