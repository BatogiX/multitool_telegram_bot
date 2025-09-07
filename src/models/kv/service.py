from models.kv.base import BaseKeyValue, BaseKeyValueGet, BaseKeyValueSet


class BaseService(BaseKeyValue):
    @property
    def key(self) -> str:
        return "service"


class SetService(BaseKeyValueSet, BaseService): ...


class GetService(BaseKeyValueGet, BaseService): ...
