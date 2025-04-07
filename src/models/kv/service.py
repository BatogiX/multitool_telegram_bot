from models.kv import BaseKeyValue, BaseKeyValueSet, BaseKeyValueGet


class BaseService(BaseKeyValue):
    @property
    def key(self) -> str:
        return "service"


class SetService(BaseKeyValueSet, BaseService): ...
class GetService(BaseKeyValueGet, BaseService): ...
