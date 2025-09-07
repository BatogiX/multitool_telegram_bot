from collections.abc import Mapping

from aiogram.fsm.storage.base import StorageKey

from models.kv.base import BaseKeyValue, BaseKeyValueDelete, BaseKeyValueGet, BaseKeyValueSet


class BaseState(BaseKeyValue):
    @property
    def key(self) -> str:
        return self.key_builder.build(self.storage_key, "state")


class SetState(BaseKeyValueSet, BaseState):
    def __init__(self, storage_key: StorageKey, value: str, expire: int | None) -> None:
        super().__init__(storage_key, value, expire)

    def dict(self) -> Mapping[str, str]: ...


class GetState(BaseKeyValueGet, BaseState): ...


class DeleteState(BaseKeyValueDelete, BaseState): ...
