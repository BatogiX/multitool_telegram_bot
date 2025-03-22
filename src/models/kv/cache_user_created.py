from typing import Dict


class CacheUserCreated:
    @staticmethod
    def key(user_id) -> str:
        return f"{user_id}:user_created"

    def __new__(cls, user_id: int) -> Dict[str, str]:
        key = cls.key(user_id)
        return {key: "1"}
