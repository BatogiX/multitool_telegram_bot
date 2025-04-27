from abc import ABC
from typing import Literal, Union

from models.kv.base import BaseKeyValueSet, BaseKeyValueGet


class BaseAction(ABC):
    action: Literal["set", "get", "delete"]
    type: Literal["data", "value"]
    data: Union[BaseKeyValueSet, BaseKeyValueGet]


class BaseDataAction(BaseAction):
    type: Literal["data"] = "data"


class BaseValueAction(BaseAction):
    type: Literal["value"] = "value"


class BaseSetAction(BaseAction):
    def __init__(self, data: BaseKeyValueSet):
        self.data = data

    action: Literal["set"] = "set"


class BaseGetAction(BaseAction):
    def __init__(self, data: BaseKeyValueGet):
        self.data = data

    action: Literal["get"] = "get"


class BaseDeleteAction(BaseAction):
    def __init__(self, data: BaseKeyValueGet):
        self.data = data

    action: Literal["delete"] = "delete"


class SetDataAction(BaseSetAction, BaseDataAction): ...


class GetFromDataAction(BaseGetAction, BaseDataAction): ...


class SetAction(BaseSetAction, BaseValueAction): ...


class GetAction(BaseGetAction, BaseValueAction): ...


class DeleteAction(BaseDeleteAction, BaseValueAction): ...
