from models.kv.base import BaseKeyValueGet, BaseKeyValue, BaseKeyValueSet


class BaseInputFormat(BaseKeyValue):
    @property
    def key(self) -> str:
        return "pm_input_format"


class SetInputFormat(BaseKeyValueSet, BaseInputFormat): ...


class GetInputFormat(BaseKeyValueGet, BaseInputFormat): ...
