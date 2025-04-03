from typing import Optional

from aiogram.fsm.storage.base import DefaultKeyBuilder, StorageKey


class BaseState:
    key_builder = DefaultKeyBuilder()

    @classmethod
    def key(cls, storage_key: StorageKey) -> str:
        return cls.key_builder.build(storage_key, "state")


class SetState(BaseState):
    @staticmethod
    def batch(state_value: Optional[str]):
        return {"data": state_value, "type": "state"}


class GetState(BaseState):
    @staticmethod
    def batch():
        return {"data": "get", "type": "state"}
