from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING, Any

from aiogram.fsm.storage.base import BaseStorage

if TYPE_CHECKING:
    from helpers.pwd_mgr_helper.pwd_mgr_crypto import EncryptedRecord


class AbstractDatabase(ABC):
    """Base abstract class for all DBs."""

    @abstractmethod
    async def connect(self) -> None:
        """Method for establishing a connection to the database."""

    @abstractmethod
    async def close(self) -> None:
        """Method for closing a connection."""


class AbstractKeyValueDatabase(AbstractDatabase):
    """Abstract class for key-value storage (Redis, Memcached)."""
    storage: BaseStorage

    @abstractmethod
    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> None:
        """
        Sets a value with an optional expiration time.

        :param key: The key to store the value under.
        :param value: The value to store.
        :param expire: Optional expiration time in seconds.
        """

    @abstractmethod
    async def get(self, key: str) -> Optional[str]:
        """
        Gets a value.

        :param key: The key to retrieve.
        :return: The stored value or None if not found.
        """


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
    async def create_user_if_not_exists(self, user_id: int, user_name: str, full_name: str) -> None:
        """Create a new user in the database."""

    @abstractmethod
    async def get_services(self, user_id: int, offset: int, limit: int) -> list[str]:
        """Get all services for a user."""

    @abstractmethod
    async def create_password(self, user_id: int, service: str, ciphertext: bytes) -> None:
        """Create a new service for a user."""

    @abstractmethod
    async def get_passwords(self, user_id: int, service: str, offset: int, limit: int) -> list[EncryptedRecord]:
        """Get all passwords of service for a user."""

    @abstractmethod
    async def get_rand_password(self, user_id: int) -> Optional[EncryptedRecord]:
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
    async def import_passwords(self, user_id: int, encrypted_records: list[EncryptedRecord]) -> None:
        """Import passwords for a user."""

    @abstractmethod
    async def export_passwords(self, user_id: int) -> Optional[EncryptedRecord]:
        """Import passwords for a user."""

    @abstractmethod
    async def inline_search_service(self, user_id: int, service: str, limit: int) -> list[str]:
        """Search for passwords of service for a user."""