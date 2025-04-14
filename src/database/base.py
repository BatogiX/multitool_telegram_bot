from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING, Any, Union, Coroutine, Type

from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import BaseStorage, StorageKey


from models.actions import BaseAction, SetDataAction, SetAction, GetFromDataAction, GetAction, DeleteAction
from models.kv import SetState, SetMessageIdToDelete, SetService, SetHashType, SetInputFormat, SetPasswordsOffset, \
    SetServicesOffset, SetCacheUserCreated, GetState, GetMessageIdToDelete, GetService, GetInputFormat, GetHashType, \
    GetPasswordsOffset, GetServicesOffset, GetCacheUserCreated, SetData
from config import bot_cfg, key_value_db_cfg
from models.kv.base import BaseKeyValueSet, BaseKeyValueGet

if TYPE_CHECKING:
    from helpers.pwd_mgr_helper import EncryptedRecord


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

    async def set_state(self, state_value: str, state: FSMContext, expire: Optional[int] = state_ttl) -> None:
        await self._set(SetState(state.key, state_value, expire))

    async def set_message_id_to_delete(self, msg_id: int, state: FSMContext, expire: Optional[int] = data_ttl) -> None:
        await self._set_data(SetMessageIdToDelete(state.key, msg_id, expire))

    async def set_service(self, service_name: str, state: FSMContext, expire: Optional[int] = data_ttl) -> None:
        await self._set_data(SetService(state.key, service_name, expire))

    async def set_hash_type(self, hash_type: str, state: FSMContext, expire: Optional[int] = data_ttl) -> None:
        await self._set_data(SetHashType(state.key, hash_type, expire))

    async def set_input_format_text(self, text: str, state: FSMContext, expire: Optional[int] = data_ttl) -> None:
        await self._set_data(SetInputFormat(state.key, text, expire))

    async def set_pwds_offset(self, offset: int, state: FSMContext, expire: Optional[int] = data_ttl) -> None:
        await self._set_data(SetPasswordsOffset(state.key, offset, expire))

    async def set_services_offset(self, offset: int, state: FSMContext, expire: Optional[int] = data_ttl) -> None:
        await self._set_data(SetServicesOffset(state.key, offset, expire))

    async def set_cache_user_created(self, state: FSMContext, expire: Optional[int] = 86400) -> None:
        await self._set(SetCacheUserCreated(state.key, "1", expire))

    async def get_state(self, state: FSMContext) -> Optional[str]:
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

    async def _set_data(self, obj: BaseKeyValueSet) -> None:
        current_data = await self._get_data(obj)
        current_data.update(obj.dict())
        await self._set(SetData(obj.storage_key, json.dumps(current_data)))

    async def _get_from_data(self, obj: BaseKeyValueGet) -> Optional[Any]:
        current_data = await self._get_data(obj)
        return current_data.get(obj.key, None)

    def _parse_coroutine(self, coro: Coroutine) -> BaseAction:
        state, value, expire = self._parse_args(coro)
        method = coro.cr_code.co_names[0]
        cls_name = coro.cr_code.co_names[1]
        cls = globals()[cls_name]
        coro.close()

        if method == self._set_data.__name__:
            cls: Type[BaseKeyValueSet]
            return SetDataAction(data=cls(state.key, value, expire=expire))

        elif method == self._set.__name__:
            cls: Type[BaseKeyValueSet]
            return SetAction(data=cls(state.key, value, expire=expire))

        elif method == self._get_from_data.__name__:
            cls: Type[BaseKeyValueGet]
            return GetFromDataAction(data=cls(state.key))

        elif method == self._get.__name__:
            cls: Type[BaseKeyValueGet]
            return GetAction(data=cls(state.key))

        elif method == self._delete.__name__:
            cls: Type[BaseKeyValueGet]
            return DeleteAction(data=cls(state.key))

        else:
            raise Exception(f"Unknown method {method}")

    @staticmethod
    def _parse_args(coro: Coroutine) -> tuple[FSMContext, Optional[str | int], Optional[int]]:
        state, value, expire = None, None, None
        for k, v in coro.cr_frame.f_locals.items():  # parsing arguments to find value for set actions
            if k == "self":
                continue
            elif k == "state":
                state = v
            elif k == "expire":
                expire = v
            else:
                value = v
        return state, value, expire

    async def _handle_storage_data(self, data: list[Optional[str]], actions: list[Union[SetDataAction, GetFromDataAction]], storage_key: StorageKey) -> tuple[Any, ...]:
        current_data = {}
        idx = 0
        for i, item in enumerate(data):
            if item[0] != "{":
                continue
            idx = i
            data.pop(idx)
            current_data = json.loads(item)
            break

        storage_dicts = {}
        for action in actions:
            if action.action == SetAction.action:
                action: SetDataAction
                storage_dicts.update(action.data.dict())
                data.insert(idx, "True")
                idx += 1
            elif action.action == GetAction.action:
                action: GetFromDataAction
                data.insert(idx, current_data.get(action.data.key, None))
                idx += 1

        if storage_dicts:
            current_data.update(storage_dicts)
            await self._set(SetData(storage_key, json.dumps(current_data)))
        return tuple(data)


class AbstractRelationDatabase(AbstractDatabase):
    """Abstract class for relational databases."""

    @abstractmethod
    async def create_user_if_not_exists(self, user_id: int, user_name: str, full_name: str, state: FSMContext) -> None:
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