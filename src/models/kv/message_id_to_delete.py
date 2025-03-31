from typing import Dict


class MessageIdToDelete:
    key: str = "message_id_to_delete_data"

    def __new__(cls, message_id: int) -> Dict[str, int]:
        return {cls.key: message_id}
