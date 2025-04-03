from typing import Dict


class MessageIdToDelete:
    key = "message_id_to_delete"

    def __new__(cls, message_id: int) -> Dict[str, int]:
        return {cls.key: message_id}
