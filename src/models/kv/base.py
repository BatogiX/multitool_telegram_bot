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


class BaseKeyValueGet(BaseKeyValue, ABC): ...


class BaseKeyValueSet(BaseKeyValue, ABC):
    def __init__(self, storage_key: StorageKey, value: Union[str, int], expire: Optional[int] = None):
        super().__init__(storage_key)
        self.value = value
        self.expire = expire

    def create(self) -> dict:
        return {self.key: self.value}
