from typing import Union

from aiogram.fsm.storage.base import StorageKey

from config import key_value_db_cfg
from models.kv.base import BaseKeyValueGet, BaseKeyValue, BaseKeyValueSet


class BaseData(BaseKeyValue):
    @property
    def key(self) -> str:
        return self.key_builder.build(self.storage_key, "data")


class SetData(BaseKeyValueSet, BaseData):
    def __init__(self, storage_key: StorageKey, value: Union[str, int]):
        super().__init__(storage_key, value, key_value_db_cfg.data_ttl)


class GetData(BaseKeyValueGet, BaseData): ...
