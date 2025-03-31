from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING, Any

from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import BaseStorage, KeyBuilder, DefaultKeyBuilder

from config import bot_cfg
from models.kv import *

if TYPE_CHECKING:
    from helpers import PasswordManagerHelper
    EncryptedRecord = PasswordManagerHelper.EncryptedRecord


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
    key_builder: KeyBuilder = DefaultKeyBuilder()

    @staticmethod
    async def set_values(state: FSMContext, *dicts: dict[str, Any]) -> Any:
        data = dict()
        for d in dicts:
            data.update(d)
        await state.update_data(data)

    @staticmethod
    async def set_message_id_to_delete(message_id: int, state: FSMContext) -> None:
        await state.update_data(MessageIdToDelete(message_id))

    @staticmethod
    async def set_service(service_name: str, state: FSMContext) -> None:
        await state.update_data(Service(service_name))

    @staticmethod
    async def set_hash_type(hash_type: str, state: FSMContext) -> None:
        await state.update_data(HashType(hash_type))

    @staticmethod
    async def set_pm_input_format_text(text: str, state: FSMContext) -> None:
        await state.update_data(PasswordManagerInputFormat(text))

    @staticmethod
    async def set_pm_pwd_offset(offset: int, state: FSMContext) -> None:
        await state.update_data(PasswordManagerPasswordsOffset(offset))

    @staticmethod
    async def set_pm_services_offset(offset: int, state: FSMContext) -> None:
        await state.update_data(PasswordManagerServicesOffset(offset))

    async def set_cache_user_created(self, user_id: int) -> None:
        await self._set(CacheUserCreated(user_id), expire=86400)

    @abstractmethod
    async def get_values(self, *keys: str, state: FSMContext) -> tuple[Any]: ...

    @staticmethod
    async def get_message_id_to_delete(state: FSMContext) -> int:
        return await state.get_value(MessageIdToDelete.key)

    @staticmethod
    async def get_service(state: FSMContext) -> str:
        return await state.get_value(Service.key)

    @staticmethod
    async def get_hash_type(state: FSMContext) -> str:
        return await state.get_value(HashType.key)

    @staticmethod
    async def get_pm_input_format_text(state: FSMContext) -> str:
        return await state.get_value(PasswordManagerInputFormat.key)

    @staticmethod
    async def get_pm_pwd_offset(state: FSMContext) -> int:
        return await state.get_value(PasswordManagerPasswordsOffset.key)

    @staticmethod
    async def get_pm_services_offset(state: FSMContext) -> int:
        return await state.get_value(PasswordManagerServicesOffset.key)

    async def get_cache_user_created(self, user_id: int) -> Optional[str]:
        return await self._get(CacheUserCreated.key(user_id))

    @abstractmethod
    async def _set(self, data: dict[str, Any], expire: Optional[int] = None) -> None:
        """
        Sets a value with an optional expiration time.

        :param data: Contains key and value
        :param expire: Optional expiration time in seconds.
        """

    @abstractmethod
    async def _get(self, key: str) -> Optional[Any]:
        """
        Gets a value.

        :param key: The key to retrieve.
        :return: The stored value or None if not found.
        """


class AbstractRelationDatabase(AbstractDatabase):
    """Abstract class for relational databases."""

    @abstractmethod
    async def create_user_if_not_exists(self, user_id: int, user_name: str, full_name: str) -> None:
        """Create a new user in the database."""

    @abstractmethod
    async def get_services(self, user_id: int, offset: int, limit: int = bot_cfg.dynamic_buttons_limit) -> Optional[list[str]]:
        """Get all services for a user."""

    @abstractmethod
    async def create_password(self, user_id: int, service: str, ciphertext: str) -> None:
        """Create a new service for a user."""

    @abstractmethod
    async def get_passwords(self, user_id: int, service: str, offset: int, limit: int = bot_cfg.dynamic_buttons_limit) -> list[EncryptedRecord]:
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
    async def delete_password(self, user_id: int, service: str, ciphertext: str) -> None:
        """Delete a password for a user."""

    @abstractmethod
    async def import_passwords(self, user_id: int, encrypted_records: list[EncryptedRecord]) -> None:
        """Import passwords for a user."""

    @abstractmethod
    async def export_passwords(self, user_id: int) -> Optional[EncryptedRecord]:
        """Import passwords for a user."""

    @abstractmethod
    async def inline_search_service(self, user_id: int, service: str, limit: int = bot_cfg.dynamic_buttons_limit) -> Optional[list[str]]:
        """Search for passwords of service for a user."""

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
    async def _init_db(self) -> None:
        """Initialize database."""