from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Literal, final, override

from models.kv.base import BaseKeyValueDelete, BaseKeyValueGet, BaseKeyValueSet


class BaseAction(ABC):
    @property
    @abstractmethod
    def action(self) -> Literal["set", "get", "delete"]: ...


class BaseType(ABC):
    @property
    @abstractmethod
    def type(self) -> Literal["data", "value"]: ...


class BaseData[DataT](ABC):
    _data: DataT

    def __init__(self, data: DataT) -> None:
        self._data = data

    @property
    def data(self) -> DataT:
        return self._data


class BaseSetAction(BaseData[BaseKeyValueSet], BaseAction, ABC):
    @property
    @override
    def action(self) -> Literal["set"]:
        return "set"


class BaseGetAction(BaseData[BaseKeyValueGet], BaseAction, ABC):
    @property
    @override
    def action(self) -> Literal["get"]:
        return "get"


class BaseDeleteAction(BaseData[BaseKeyValueDelete], BaseAction, ABC):
    @property
    @override
    def action(self) -> Literal["delete"]:
        return "delete"


class BaseDataAction(BaseType, ABC):
    @property
    @override
    def type(self) -> Literal["data"]:
        return "data"


class BaseValueAction(BaseType, ABC):
    @property
    @override
    def type(self) -> Literal["value"]:
        return "value"


@final
class SetDataAction(BaseSetAction, BaseDataAction): ...


@final
class GetFromDataAction(BaseGetAction, BaseDataAction): ...


@final
class SetAction(BaseSetAction, BaseValueAction): ...


@final
class GetAction(BaseGetAction, BaseValueAction): ...


@final
class DeleteAction(BaseDeleteAction, BaseValueAction): ...
