from models.kv.base import BaseKeyValueGet, BaseKeyValue, BaseKeyValueSet


class BasePasswordsOffset(BaseKeyValue):
    @property
    def key(self) -> str:
        return "pwds_offset"


class SetPasswordsOffset(BaseKeyValueSet, BasePasswordsOffset): ...


class GetPasswordsOffset(BaseKeyValueGet, BasePasswordsOffset): ...
