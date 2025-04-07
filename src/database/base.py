from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING, Any, Union, Coroutine, Type

from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import BaseStorage

from models.kv import *
from config import bot_cfg, key_value_db_cfg

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
    state_ttl: Optional[int] = key_value_db_cfg.state_ttl
    data_ttl: Optional[int] = key_value_db_cfg.data_ttl

    @abstractmethod
    async def _set(self, obj: BaseKeyValueSet) -> None:
        """
        Sets a value with an optional expiration time.
        """

    @abstractmethod
    async def _get(self, obj: BaseKeyValueGet) -> Optional[Any]:
        """
        Gets a value.

        :return: The stored value or None if not found.
        """

    @abstractmethod
    async def _delete(self, obj: BaseKeyValueGet): ...

    @abstractmethod
    async def execute_batch(self, *coroutines: Coroutine) -> tuple[Any, ...]: ...

    async def _set_data(self, obj: BaseKeyValueSet) -> None:
        current_data = await self._get_data(obj)
        current_data.update(obj.create())
        await self._set(SetData(obj.storage_key, json.dumps(current_data)))

    async def _get_from_data(self, obj: BaseKeyValueGet) -> Optional[Any]:
        current_data = await self._get_data(obj)
        return current_data.get(obj.key, None)

    async def set_state(self, state_value: str, state: FSMContext) -> None:
        await self._set(SetState(state.key, state_value))

    async def set_message_id_to_delete(self, msg_id: int, state: FSMContext) -> None:
        await self._set_data(SetMessageIdToDelete(state.key, msg_id))

    async def set_service(self, service_name: str, state: FSMContext) -> None:
        await self._set_data(SetService(state.key, service_name))

    async def set_hash_type(self, hash_type: str, state: FSMContext) -> None:
        await self._set_data(SetHashType(state.key, hash_type))

    async def set_input_format_text(self, text: str, state: FSMContext) -> None:
        await self._set_data(SetInputFormat(state.key, text))

    async def set_pwds_offset(self, offset: int, state: FSMContext) -> None:
        await self._set_data(SetPasswordsOffset(state.key, offset))

    async def set_services_offset(self, offset: int, state: FSMContext) -> None:
        await self._set_data(SetServicesOffset(state.key, offset))

    async def set_cache_user_created(self, state: FSMContext) -> None:
        await self._set(SetCacheUserCreated(state.key, "1", expire=86400))

    async def get_state(self, state: FSMContext):
        await self._get(GetState(state.key))

    async def get_message_id_to_delete(self, state: FSMContext) -> Union[int]:
        return await self._get_from_data(GetMessageIdToDelete(state.key))

    async def get_service(self, state: FSMContext) -> str:
        return await self._get_from_data(GetService(state.key))

    async def get_hash_type(self, state: FSMContext) -> str:
        return await self._get_from_data(GetHashType(state.key))

    async def get_input_format_text(self, state: FSMContext) -> str:
        return await self._get_from_data(GetInputFormat(state.key))

    async def get_pwds_offset(self, state: FSMContext) -> int:
        return await self._get_from_data(GetPasswordsOffset(state.key))

    async def get_services_offset(self, state: FSMContext) -> int:
        return await self._get_from_data(GetServicesOffset(state.key))

    async def get_cache_user_created(self, state: FSMContext) -> Optional[str]:
        return await self._get(GetCacheUserCreated(state.key))

    async def clear_state(self, state: FSMContext) -> None:
        await self._delete(GetState(state.key))

    async def _get_data(self, obj: Union[BaseKeyValueSet, BaseKeyValueGet]) -> dict:
        current_data = await self._get(obj)
        if current_data is None:
            return {}
        return json.loads(current_data)

    def _parse_coroutine(self, coro: Coroutine) -> BaseAction:
        fsm_context, value = self._parse_args(coro)
        method = coro.cr_code.co_names[0]
        cls_name = coro.cr_code.co_names[1]
        coro.close()
        cls = globals()[cls_name]

        if method == self._set_data.__name__:
            cls: Type[SetData]
            return SetDataAction(cls(fsm_context.key, value))

        elif method == self._set.__name__:
            cls: Type[BaseKeyValueSet]
            return SetAction(cls(fsm_context.key, value, expire=ex))

        elif method == self._get_from_data.__name__:
            cls: Type[GetData]
            return GetFromDataAction(cls(fsm_context.key))

        elif method == self._get.__name__:
            cls: Type[BaseKeyValueGet]
            return GetAction(cls(fsm_context.key))

        elif method == self._delete.__name__:
            cls: Type[BaseKeyValueGet]
            return DeleteAction(cls(fsm_context.key))

        else:
            raise Exception(f"Unknown method {method}")

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

    async def _handle_storage_data(self, data: list[Optional[str]], commands: list[BaseAction], built_storage_key: str) -> tuple[Any, ...]:
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
            await self._set(built_storage_key, json.dumps(storage_data))
        return tuple(data)


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