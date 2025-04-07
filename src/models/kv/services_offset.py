from models.kv import BaseKeyValue, BaseKeyValueSet, BaseKeyValueGet


class BaseServicesOffset(BaseKeyValue):
    @property
    def key(self) -> str:
        return "services_offset"


class SetServicesOffset(BaseKeyValueSet, BaseServicesOffset): ...
class GetServicesOffset(BaseKeyValueGet, BaseServicesOffset): ...
