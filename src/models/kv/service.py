from models.kv.base import BaseKeyValueGet, BaseKeyValue, BaseKeyValueSet


class BaseService(BaseKeyValue):
    @property
    def key(self) -> str:
        return "service"


class SetService(BaseKeyValueSet, BaseService): ...
class GetService(BaseKeyValueGet, BaseService): ...
