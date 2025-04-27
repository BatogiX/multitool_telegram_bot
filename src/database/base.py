from __future__ import annotations

import inspect
import json
from abc import ABC, abstractmethod
from functools import cached_property

from config import key_value_db_cfg
import models.kv
from models.actions import SetDataAction, SetAction, GetFromDataAction, GetAction, DeleteAction


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
    state_ttl = key_value_db_cfg.state_ttl
    data_ttl = key_value_db_cfg.data_ttl

    @abstractmethod
    async def _set(self, obj):
        """
        models.kv.Sets a value with an optional expiration time.
        """

    @abstractmethod
    async def _get(self, obj):
        """
        Gets a value.

        :return: The stored value or None if not found.
        """

    @abstractmethod
    async def _delete(self, obj): ...

    @abstractmethod
    async def execute_batch(self, *coros): ...

    async def set_state(self, state_value, state, expire = state_ttl):
        await self._set(models.kv.SetState(state.key, state_value, expire))

    async def set_message_id_to_delete(self, msg_id, state, expire = data_ttl):
        await self._set_data(models.kv.SetMessageIdToDelete(state.key, msg_id, expire))

    async def set_service(self, service_name, state, expire = data_ttl):
        await self._set_data(models.kv.SetService(state.key, service_name, expire))

    async def set_hash_type(self, hash_type, state, expire = data_ttl):
        await self._set_data(models.kv.SetHashType(state.key, hash_type, expire))

    async def set_input_format_text(self, text, state, expire = data_ttl):
        await self._set_data(models.kv.SetInputFormat(state.key, text, expire))

    async def set_pwds_offset(self, offset, state, expire = data_ttl):
        await self._set_data(models.kv.SetPasswordsOffset(state.key, offset, expire))

    async def set_services_offset(self, offset, state, expire = data_ttl):
        await self._set_data(models.kv.SetServicesOffset(state.key, offset, expire))

    async def set_cache_user_created(self, state, value = "1", expire = 86400):
        await self._set(models.kv.SetCacheUserCreated(state.key, value, expire))

    async def get_state(self, state):
        await self._get(models.kv.GetState(state.key))

    async def get_message_id_to_delete(self, state):
        return await self._get_from_data(models.kv.GetMessageIdToDelete(state.key))

    async def get_service(self, state):
        return await self._get_from_data(models.kv.GetService(state.key))

    async def get_hash_type(self, state):
        return await self._get_from_data(models.kv.GetHashType(state.key))

    async def get_input_format_text(self, state):
        return await self._get_from_data(models.kv.GetInputFormat(state.key))

    async def get_pwds_offset(self, state):
        return await self._get_from_data(models.kv.GetPasswordsOffset(state.key))

    async def get_services_offset(self, state):
        return await self._get_from_data(models.kv.GetServicesOffset(state.key))

    async def get_cache_user_created(self, state):
        return await self._get(models.kv.GetCacheUserCreated(state.key))

    async def clear_state(self, state):
        await self._delete(models.kv.GetState(state.key))

    async def _get_data(self, obj):
        current_data = await self._get(obj)
        if current_data is None:
            return {}
        return json.loads(current_data)

    async def _set_data(self, obj):
        current_data = await self._get_data(obj)
        current_data.update(obj.dict())
        await self._set(models.kv.SetData(obj.storage_key, json.dumps(current_data)))

    async def _get_from_data(self, obj):
        current_data = await self._get_data(obj)
        return current_data.get(obj.key, None)

    def _parse_coroutine(self, coro):
        state, value, expire = self._parse_args(coro)
        method, kv_cls = self._parse_names(coro)
        coro.close()

        Action = self._method_to_action_map.get(method)  # type: ignore
        if value is None:
            return Action(kv_cls(state.key))  # GetAction/GetFromDataAction/DeleteAction
        else:
            return Action(kv_cls(state.key, value, expire))  # SetAction/SetDataAction


    @staticmethod
    def _parse_args(coro):
        args = inspect.getargvalues(coro.cr_frame)
        state, value, expire = None, None, None
        for k, v in args.locals.items():  # parsing arguments to find value for set actions
            if k == "self":
                continue
            elif k == "state":
                state = v
            elif k == "expire":
                expire = v
            else:
                value = v
        return state, value, expire

    @cached_property
    def _method_to_action_map(self):
        return {
            self._set.__name__: SetAction,
            self._set_data.__name__: SetDataAction,
            self._get.__name__: GetAction,
            self._get_from_data.__name__: GetFromDataAction,
            self._delete.__name__: DeleteAction
        }

    def _parse_names(self, coro):
        methods = self._method_to_action_map.keys()  # type: ignore
        names = coro.cr_code.co_names
        for i ,name in enumerate(names):
            if name in methods:
                # e.g await self._set(models.kv.SetState(state.key, state_value, expire))
                # returns _set, SetState
                return names[i], getattr(models.kv, names[i+3])
        raise Exception(f"Unknown method in coroutine {coro}")

    async def _handle_storage_data(self, data, actions, storage_key):
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
            if action.action == SetDataAction.action:
                action: SetDataAction
                storage_dicts.update(action.data.dict())
                data.insert(idx, "True")
                idx += 1
            elif action.action == GetFromDataAction.action:
                action: GetFromDataAction
                data.insert(idx, current_data.get(action.data.key, None))
                idx += 1

        if storage_dicts:
            current_data.update(storage_dicts)
            await self._set(models.kv.SetData(storage_key, json.dumps(current_data)))
        return tuple(data)


class AbstractRelationDatabase(AbstractDatabase):
    """Abstract class for relational databases."""

    @abstractmethod
    async def create_user_if_not_exists(
        self, user_id, user_name, full_name, state):
        """Create a new user in the database."""

    @abstractmethod
    async def get_services(self, user_id, offset, limit):
        """Get all services for a user."""

    @abstractmethod
    async def create_password(self, user_id, service, ciphertext):
        """Create a new service for a user."""

    @abstractmethod
    async def get_passwords(self, user_id, service, offset, limit):
        """Get all passwords of service for a user."""

    @abstractmethod
    async def get_rand_password(self, user_id):
        """Get a random passwords record for a user."""

    @abstractmethod
    async def change_service(self, new_service, user_id, old_service):
        """Change service name for a user."""

    @abstractmethod
    async def delete_services(self, user_id):
        """Delete all services for a user."""

    @abstractmethod
    async def delete_service(self, user_id, service):
        """Delete a service for a user."""

    @abstractmethod
    async def delete_password(self, user_id, service, ciphertext):
        """Delete a password for a user."""

    @abstractmethod
    async def update_credentials(self, user_id, service, current_ciphertext, new_ciphertext):
        """Updates login and/or password for record"""

    @abstractmethod
    async def import_passwords(self, user_id, encrypted_records):
        """Import passwords for a user."""

    @abstractmethod
    async def export_passwords(self, user_id):
        """Import passwords for a user."""

    @abstractmethod
    async def inline_search_service(self, user_id, service, limit):
        """Search for passwords of service for a user."""

    @abstractmethod
    async def get_salt(self, user_id): ...

    @abstractmethod
    async def _execute(self, query, *args):
        """Execute an SQL query without returning a result (INSERT, UPDATE, DELETE)."""

    @abstractmethod
    async def _fetch_row(self, query, *args):
        """Get one record from the database."""

    @abstractmethod
    async def _fetch_value(self, query, *args):
        """Get a single value from the database."""

    @abstractmethod
    async def _fetch_all(self, query, *args):
        """Get a list of records from the database."""

    @abstractmethod
    async def _init_db(self) -> None:
        """Initialize database."""
