from abc import ABC, abstractmethod

from pydantic_settings import BaseSettings

from models.db_record.password_record import EncryptedRecord, PasswordRecord


class AbstractDatabase(ABC):
    """Base abstract class for all DBs."""

    def __init__(self, config: BaseSettings):
        self._c = config

    @abstractmethod
    async def connect(self):
        """Method for establishing a connection to the database."""

    @abstractmethod
    async def disconnect(self):
        """Method for closing a connection."""


class AbstractKeyValueDatabase(AbstractDatabase):
    """Abstract class for key-value storage (Redis, Memcached)."""

    @abstractmethod
    async def get(self, key: str):
        """Get value by key."""

    @abstractmethod
    async def set(self, key: str, value: str, expire: int = None):
        """Set a value by key with expiration option."""

    @abstractmethod
    async def delete(self, key: str):
        """Delete key from storage."""


class AbstractRelationDatabase(AbstractDatabase):
    """Abstract class for relational databases."""

    @abstractmethod
    async def _execute(self, query: str, *args) -> None:
        """Execute an SQL query without returning a result (INSERT, UPDATE, DELETE)."""

    @abstractmethod
    async def _fetch_row(self, query: str, *args) -> any:
        """Get one record from the database."""

    @abstractmethod
    async def _fetch_value(self, query: str, *args) -> any:
        """Get a single value from the database."""

    @abstractmethod
    async def _fetch_all(self, query: str, *args) -> any:
        """Get a list of records from the database."""

    @abstractmethod
    async def init_db(self) -> None:
        """Initialize database."""

    @abstractmethod
    async def create_user_if_not_exists(self, user_id: int, user_name: str, full_name: str, salt: bytes) -> None:
        """Create a new user in the database."""

    @abstractmethod
    async def get_services(self, user_id: int, offset: int, limit: int) -> list[str]:
        """Get all services for a user."""

    @abstractmethod
    async def create_password(self, user_id: int, service: str, iv: bytes, tag: bytes, ciphertext: bytes) -> None:
        """Create a new service for a user."""

    @abstractmethod
    async def get_salt(self, user_id: int) -> bytes:
        """Get salt for a user."""

    @abstractmethod
    async def get_passwords(self, user_id: int, service: str, offset: int, limit: int) -> list[EncryptedRecord]:
        """Get all passwords of service for a user."""

    @abstractmethod
    async def get_rand_password(self, user_id: int) -> EncryptedRecord | None:
        """Get a random passwords record for a user."""

    @abstractmethod
    async def change_service(self, new_service: str, user_id: int, old_service: str) -> None:
        """Change service name for a user."""

    @abstractmethod
    async def delete_services(self, user_id: int) -> None:
        """Delete all services for a user."""

    @abstractmethod
    async def delete_service(self, user_id: int, service: str) -> None:
        """Delete a service for a user."""

    @abstractmethod
    async def delete_password(self, user_id: int, service: str, ciphertext: bytes) -> None:
        """Delete a password for a user."""

    @abstractmethod
    async def import_passwords(self, user_id: int, pwd_records: list[PasswordRecord]) -> None:
        """Import passwords for a user."""

    @abstractmethod
    async def export_passwords(self, user_id: int) -> list[PasswordRecord] | None:
        """Import passwords for a user."""

    @abstractmethod
    async def inline_search_service(self, user_id: int, service: str, limit: int) -> list[str]:
        """Search for passwords of service for a user."""