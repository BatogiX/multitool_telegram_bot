from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING, Any, Union, Coroutine

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

    @abstractmethod
    async def execute_batch(self, *coroutines: Coroutine) -> tuple[Any, ...]: ...

    async def set_state(self, state_value: State, state: FSMContext) -> None:
        await self._set_value(SetState.key(state.key), state_value.state)

    async def set_message_id_to_delete(self, msg_id: int, state: FSMContext) -> None:
        await self._update_data(MessageIdToDelete(msg_id), state.key)

    async def set_service(self, service_name: str, state: FSMContext) -> None:
        await self._update_data(Service(service_name), state.key)

    async def set_hash_type(self, hash_type: str, state: FSMContext) -> None:
        await self._update_data(HashType(hash_type), state.key)

    async def set_pm_input_format_text(self, text: str, state: FSMContext) -> None:
        await self._update_data(PasswordManagerInputFormat(text), state.key)

    async def set_pm_pwd_offset(self, offset: int, state: FSMContext) -> None:
        await self._update_data(PasswordManagerPasswordsOffset(offset), state.key)

    async def set_pm_services_offset(self, offset: int, state: FSMContext) -> None:
        await self._update_data(PasswordManagerServicesOffset(offset), state.key)

    async def set_cache_user_created(self, user_id: int) -> None:
        await self._set_value(CacheUserCreated.key(user_id), user_id, expire=86400)

    async def get_state(self, state: FSMContext):
        await self._get_value(BaseState.key(state.key))

    async def get_message_id_to_delete(self, storage_key: StorageKey) -> Union[int]:
        return await self._get_value_from_data(MessageIdToDelete.key, storage_key)

    async def get_service(self, state: FSMContext) -> str:
        return await self._get_value_from_data(Service.key, state.key)

    async def get_hash_type(self, state: FSMContext) -> str:
        return await self._get_value_from_data(HashType.key, state.key)

    async def get_pm_input_format_text(self, state: FSMContext) -> str:
        return await self._get_value_from_data(PasswordManagerInputFormat.key, state.key)

    async def get_pm_pwd_offset(self, state: FSMContext) -> int:
        return await self._get_value_from_data(PasswordManagerPasswordsOffset.key, state.key)

    async def get_pm_services_offset(self, state: FSMContext) -> int:
        return await self._get_value_from_data(PasswordManagerServicesOffset.key, state.key)

    async def get_cache_user_created(self, user_id: int) -> Optional[str]:
        return await self._get_value(CacheUserCreated.key(user_id))

    async def clear_state(self, state: FSMContext) -> None:
        await self._delete(BaseState.key(state.key))

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

    def _parse_coroutine(self, coro: Coroutine) -> Action:
        fsm_context, value = self._parse_args(coro)
        method = coro.cr_code.co_names[0]
        cls_name = coro.cr_code.co_names[1]
        cls = globals()[cls_name]

        method_to_action_mapping = {
            self._update_data.__name__: lambda: UpdateDataAction(data=cls(value), storage_key=fsm_context.key),
            self._set_value.__name__: lambda: self._create_set_value_action(cls, value, fsm_context),
            self._get_value_from_data.__name__: lambda: GetValueFromDataAction(data=cls.key, storage_key=fsm_context.key),
            self._get_value.__name__: lambda: GetValueAction(data=cls.key, storage_key=fsm_context.key),
            self._delete.__name__: lambda: self._create_delete_action(cls, fsm_context)
        }

        try:
            action = method_to_action_mapping.get(method)
            if action:
                return action()
            else:
                raise Exception(f"Unknown method {method} in coroutine {coro}")
        finally:
            coro.close()

    @staticmethod
    def _parse_args(coro: Coroutine) -> tuple[FSMContext, Optional[str | int]]:
        state, value = None, None
        for k, v in coro.cr_frame.f_locals.items():  # parsing arguments to find value for set/update commands
            if k == "self" :
                continue
            elif k == "state":
                state = v
            else:
                value = v
        return state, value

    @staticmethod
    def _create_set_value_action(cls, value, fsm_context: FSMContext):
        if cls == SetState:
            return SetStateAction(data=cls(value.state, fsm_context.key), storage_key=fsm_context.key)
        return SetValueAction(data=cls(value), storage_key=fsm_context.key)

    @staticmethod
    def _create_delete_action(cls, fsm_context: FSMContext):
        key = cls.key
        if cls == BaseState:
            return DeleteStateAction(data=key(fsm_context.key), storage_key=fsm_context.key)
        return DeleteStateAction(data=key, storage_key=fsm_context.key)

    async def _handle_storage_data(self, data: list[Optional[str]], commands: list[Action], built_storage_key: str) -> tuple[Any, ...]:
        storage_data = {}
        idx = 0
        for d in data:
            if d[0] != "{":
                continue
            idx = data.index(d)
            data.pop(idx)
            storage_data = json.loads(d)
            break

        storage_dicts = {}
        for cmd in commands:
            if cmd.type != "data":
                continue
            if isinstance(cmd.data, dict):
                storage_dicts.update(cmd.data)
                data.insert(idx, None)
                idx += 1
            elif isinstance(cmd.data, str):
                data.insert(idx, storage_data.get(cmd.data, None))
                idx += 1

        if storage_dicts:
            storage_data.update(storage_dicts)
            await self._set_value(built_storage_key, json.dumps(storage_data))
        return tuple(data)

    @abstractmethod
    async def _delete(self, key: str): ...

    async def _update_data(self, data: dict[str, Any], storage_key: StorageKey) -> None:
        key = self.key_builder.build(storage_key)
        current_data = await self._get_data(key)
        current_data.update(data)
        await self._set_value(key, json.dumps(current_data))

    async def _get_value_from_data(self, key: str, storage_key: StorageKey) -> Optional[Any]:
        current_data = await self._get_data(self.key_builder.build(storage_key))
        return current_data.get(key, None)

    async def _get_data(self, key: str) -> dict:
        current_data = await self._get_value(key)
        if current_data is None:
            return {}
        return json.loads(current_data)


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