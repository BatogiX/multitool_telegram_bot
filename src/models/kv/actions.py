from abc import ABC
from typing import Literal

from models.kv import BaseKeyValueSet, BaseKeyValueGet, SetData, GetData


class BaseAction(ABC):
    type: Literal["data", "value"]
    action: Literal["set", "get", "delete"]


class BaseGetAction(BaseAction, ABC):
    action: Literal["get"] = "get"


class BaseSetAction(BaseAction, ABC):
    action: Literal["set"] = "set"


class BaseDeleteAction(BaseAction, ABC):
    action: Literal["delete"] = "delete"


class BaseDataAction(BaseAction, ABC):
    type: Literal["data"] = "data"


class BaseValueAction(BaseAction, ABC):
    type: Literal["value"] = "value"


class SetDataAction(BaseSetAction, BaseDataAction):
    def __init__(self, data: SetData):
        self.data = data


class GetFromDataAction(BaseGetAction, BaseDataAction):
    def __init__(self, data: GetData):
        self.data = data


class SetAction(BaseSetAction, BaseValueAction):
    def __init__(self, data: BaseKeyValueSet):
        self.data = data


class GetAction(BaseGetAction, BaseValueAction):
    def __init__(self, data: BaseKeyValueGet):
        self.data = data


class DeleteAction(BaseDeleteAction, BaseValueAction):
    def __init__(self, data: BaseKeyValueGet):
        self.data = data
