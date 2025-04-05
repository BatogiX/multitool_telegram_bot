from typing import Dict

from models.kv import BaseKeyValue


class MessageIdToDelete(BaseKeyValue):
    key = "message_id_to_delete"

    def __new__(cls, message_id: int) -> Dict[str, int]:
        return {cls.key: message_id}
