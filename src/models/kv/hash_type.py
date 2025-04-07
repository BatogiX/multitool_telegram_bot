from models.kv import BaseKeyValue, BaseKeyValueSet, BaseKeyValueGet


class BaseHashType(BaseKeyValue):
    @property
    def key(self) -> str:
        return "hash_type"


class SetHashType(BaseKeyValueSet, BaseHashType): ...
class GetHashType(BaseKeyValueGet, BaseHashType): ...
