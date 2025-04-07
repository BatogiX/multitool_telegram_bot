from models.kv import BaseKeyValue, BaseKeyValueSet, BaseKeyValueGet


class BasePasswordsOffset(BaseKeyValue):
    @property
    def key(self) -> str:
        return "pwds_offset"


class SetPasswordsOffset(BaseKeyValueSet, BasePasswordsOffset): ...
class GetPasswordsOffset(BaseKeyValueGet, BasePasswordsOffset): ...
