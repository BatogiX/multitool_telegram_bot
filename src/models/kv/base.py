from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from aiogram.fsm.storage.base import DefaultKeyBuilder

if TYPE_CHECKING:
    from collections.abc import Mapping

    from aiogram.fsm.storage.base import StorageKey


class BaseKeyValue(ABC):
    key_builder = DefaultKeyBuilder()

    def __init__(self, storage_key: StorageKey) -> None:
        self.storage_key = storage_key

    @property
    @abstractmethod
    def key(self) -> str: ...

    @property
    def data_key(self) -> str:
        return self.key_builder.build(self.storage_key, "data")


class BaseKeyValueSet(BaseKeyValue, ABC):
    def __init__(self, storage_key: StorageKey, value: str | int, expire: int | None) -> None:
        super().__init__(storage_key)
        self.value = value
        self.expire = expire

    def dict(self) -> Mapping[str, str | int]:
        return {self.key: self.value}


class BaseKeyValueGet(BaseKeyValue, ABC): ...


class BaseKeyValueDelete(BaseKeyValue, ABC): ...
