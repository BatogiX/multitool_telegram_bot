from models.kv.base import BaseKeyValueGet, BaseKeyValue, BaseKeyValueSet


class BaseState(BaseKeyValue):
    @property
    def key(self) -> str:
        return self.key_builder.build(self.storage_key, "state")


class SetState(BaseKeyValueSet, BaseState): ...


class GetState(BaseKeyValueGet, BaseState): ...
