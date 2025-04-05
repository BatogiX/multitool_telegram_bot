from abc import ABC
from typing import Literal, Union

from aiogram.fsm.storage.base import StorageKey


class BaseAction(ABC):
    data: Union[dict, str]
    storage_key: StorageKey

    type: Literal["data", "value"]
    action: Literal["set", "get", "delete"]


class BaseSetAction(BaseAction):
    def __init__(self, data: dict[str, Union[str, tuple]], storage_key: StorageKey):
        self.data = data
        self.storage_key = storage_key

    action: Literal["set"] = "set"


class BaseGetAction(BaseAction):
    def __init__(self, data: str, storage_key: StorageKey):
        self.data = data
        self.storage_key = storage_key

    action: Literal["get"] = "get"


class BaseDeleteAction(BaseAction):
    def __init__(self, data: str, storage_key: StorageKey):
        self.data = data
        self.storage_key = storage_key

    action: Literal["delete"] = "delete"


class BaseDataAction(BaseAction):
    type: Literal["data"] = "data"


class BaseValueAction(BaseAction):
    type: Literal["value"] = "value"


class SetDataAction(BaseSetAction, BaseDataAction): ...


class GetFromDataAction(BaseGetAction, BaseDataAction): ...


class SetAction(BaseSetAction, BaseValueAction): ...


class GetAction(BaseGetAction, BaseValueAction): ...


class DeleteAction(BaseDeleteAction, BaseValueAction): ...
