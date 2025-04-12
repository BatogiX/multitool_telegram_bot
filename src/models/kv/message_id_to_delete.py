from models.kv.base import BaseKeyValueGet, BaseKeyValue, BaseKeyValueSet


class BaseMessageIdToDelete(BaseKeyValue):
    @property
    def key(self) -> str:
        return "message_id_to_delete"

class SetMessageIdToDelete(BaseKeyValueSet, BaseMessageIdToDelete): ...
class GetMessageIdToDelete(BaseKeyValueGet, BaseMessageIdToDelete): ...
