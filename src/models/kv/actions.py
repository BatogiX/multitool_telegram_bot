from abc import ABC
from typing import Literal, Union

from aiogram.fsm.storage.base import StorageKey


class Action(ABC):
    data: Union[dict, str]
    storage_key: StorageKey

    type: Literal["data", "value", "state"]
    action: Literal["set", "get", "delete"]


class SetAction(Action):
    def __init__(self, data: dict, storage_key: StorageKey):
        self.data = data
        self.storage_key = storage_key

    action: Literal["set"] = "set"


class GetAction(Action):
    def __init__(self, data: str, storage_key: StorageKey):
        self.data = data
        self.storage_key = storage_key

    action: Literal["get"] = "get"


class DeleteAction(Action):
    def __init__(self, data: str, storage_key: StorageKey):
        self.data = data
        self.storage_key = storage_key

    action: Literal["delete"] = "delete"

class DataAction(Action):
    type: Literal["data"] = "data"


class ValueAction(Action):
    type: Literal["value"] = "value"


class StateAction(Action):
    type: Literal["state"] = "state"


class UpdateDataAction(SetAction, DataAction): ...

class GetValueFromDataAction(GetAction, DataAction): ...

class SetValueAction(SetAction, ValueAction): ...

class GetValueAction(GetAction, ValueAction): ...

class SetStateAction(SetAction, StateAction): ...

class GetStateAction(GetAction, StateAction): ...

class DeleteStateAction(DeleteAction, StateAction): ...
