class MessageToDelete:
    key: str = "message_to_delete"

    def __new__(cls, message_id: int):
        return {cls.key: message_id}
