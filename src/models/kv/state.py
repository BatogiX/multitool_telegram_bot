from aiogram.fsm.storage.base import DefaultKeyBuilder, StorageKey


class BaseState:
    key_builder = DefaultKeyBuilder()

    @classmethod
    def key(cls, storage_key: StorageKey) -> str:
        return cls.key_builder.build(storage_key, "state")


class SetState(BaseState):
    def __new__(cls, service_name: str, storage_key: StorageKey) -> dict[str, str]:
        return {cls.key(storage_key): service_name}
