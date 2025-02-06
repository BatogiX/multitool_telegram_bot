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
    async def _execute(self, query: str, *args) -> None:
        """Execute an SQL query without returning a result (INSERT, UPDATE, DELETE)."""
        pass

    @abstractmethod
    async def _fetch_row(self, query: str, *args) -> any:
        """Get one record from the database."""
        pass

    @abstractmethod
    async def _fetch_value(self, query: str, *args) -> any:
        """Get a single value from the database."""
        pass

    @abstractmethod
    async def _fetch_all(self, query: str, *args) -> any:
        """Get a list of records from the database."""
        pass

    @abstractmethod
    async def init_db(self) -> None:
        """Initialize database."""
        pass

    @abstractmethod
    async def user_exists(self, user_id: int) -> bool:
        """Check if user exists in the database."""
        pass

    @abstractmethod
    async def add_user(self, user_id: int, user_name: str, full_name: str) -> None:
        """Add a new user to the database."""
        pass