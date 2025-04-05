from models.kv import BaseKeyValue


class CacheUserCreated(BaseKeyValue):
    @staticmethod
    def key(user_id) -> str:
        return f"{user_id}:user_created"

    @classmethod
    def create(cls, user_id: int) -> dict[str, str]:
        key = cls.key(user_id)
        return {key: "1"}
