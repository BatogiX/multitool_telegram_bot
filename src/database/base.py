from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING, Any, Union, Callable, Awaitable

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.fsm.storage.base import BaseStorage, KeyBuilder, DefaultKeyBuilder, StorageKey

from models.kv import *
from config import bot_cfg

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

    async def set_state(self, state_value: Optional[State] = None, storage_key: Optional[StorageKey] = None, batch_mode: bool = False):
        state_value = state_value.state if state_value else None
        if batch_mode:
            return SetState.batch(state_value)
        await self._set_value(SetState.key(storage_key), state_value)

    async def get_state(self, storage_key: Optional[StorageKey] = None, batch_mode: bool = False):
        if batch_mode:
            return GetState.batch()
        await self._get_value(GetState.key(storage_key))

    @abstractmethod
    async def execute_batch(self, *coroutines: Callable[..., Awaitable[Union[str, dict[str, Any]]]], storage_key: StorageKey): ...

    async def set_message_id_to_delete(self, msg_id: int, storage_key: StorageKey, batch_mode: bool = False) -> Optional[dict]:
        if batch_mode:
            return {"data": {"message_id_to_delete_data": msg_id}, "type": "data"}
        await self._update_data({"message_id_to_delete_data": msg_id}, storage_key)

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
        await self._set_value(CacheUserCreated.key(user_id), user_id, expire=86400)

    async def get_message_id_to_delete(self, storage_key: StorageKey, batch_mode: bool = False) -> Union[int, dict]:
        if batch_mode:
            return {"data": "message_id_to_delete_data", "type": "data"}
        return await self._get_value_from_data("message_id_to_delete", storage_key)

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
        return await self._get_value(CacheUserCreated.key(user_id))

    @abstractmethod
    async def _set_value(self, key: str, value: Any, expire: Optional[int] = None) -> None:
        """
        Sets a value with an optional expiration time.

        :param data: Contains key and value
        :param expire: Optional expiration time in seconds.
        """

    @abstractmethod
    async def _get_value(self, key: str) -> Optional[Any]:
        """
        Gets a value.

        :param key: The key to retrieve.
        :return: The stored value or None if not found.
        """

    async def _get_data(self, key: str) -> dict:
        current_data = await self._get_value(key)
        return json.loads(current_data)

    async def _update_data(self, data: dict[str, Any], storage_key: StorageKey) -> None:
        key = self.key_builder.build(storage_key)
        current_data = await self._get_data(key)
        current_data.update(data)
        await self._set_value(key, json.dumps(current_data))

    async def _get_value_from_data(self, key: str, storage_key: StorageKey) -> Optional[Any]:
        current_data = await self._get_data(self.key_builder.build(storage_key))
        return current_data.get(key, None)

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