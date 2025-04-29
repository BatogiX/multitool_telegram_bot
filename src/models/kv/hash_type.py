from models.kv.base import BaseKeyValueGet, BaseKeyValue, BaseKeyValueSet


class BaseHashType(BaseKeyValue):
    @property
    def key(self) -> str:
        return "hash_type"


class SetHashType(BaseKeyValueSet, BaseHashType): ...


class GetHashType(BaseKeyValueGet, BaseHashType): ...
