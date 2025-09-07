from __future__ import annotations

from typing import TYPE_CHECKING

from config import NOSQL_DB_CFG
from models.kv.base import BaseKeyValue, BaseKeyValueGet, BaseKeyValueSet

if TYPE_CHECKING:
    from aiogram.fsm.storage.base import StorageKey


class BaseData(BaseKeyValue):
    @property
    def key(self) -> str:
        return self.key_builder.build(self.storage_key, "data")


class SetData(BaseKeyValueSet, BaseData):
    def __init__(self, storage_key: StorageKey, value: str) -> None:
        super().__init__(storage_key, value, NOSQL_DB_CFG.data_ttl)


class GetData(BaseKeyValueGet, BaseData): ...
