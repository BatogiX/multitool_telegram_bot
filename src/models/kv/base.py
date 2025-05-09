from abc import ABC, abstractmethod
from typing import Optional, Union

from aiogram.fsm.storage.base import StorageKey, DefaultKeyBuilder


class BaseKeyValue(ABC):
    key_builder = DefaultKeyBuilder()

    def __init__(self, storage_key: StorageKey):
        self.storage_key = storage_key

    @property
    @abstractmethod
    def key(self) -> str: ...

    @property
    def data_key(self) -> str:
        return self.key_builder.build(self.storage_key, "data")


class BaseKeyValueGet(BaseKeyValue, ABC): ...


class BaseKeyValueSet(BaseKeyValue, ABC):
    def __init__(self, storage_key: StorageKey, value: Union[str, int], expire: Optional[int]):
        super().__init__(storage_key)
        self.value = value
        self.expire = expire

    def dict(self) -> dict:
        return {self.key: self.value}
