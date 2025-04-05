from typing import Dict

from models.kv import BaseKeyValue


class HashType(BaseKeyValue):
    key = "hash_type"

    def __new__(cls, hash_type: str) -> Dict[str, str]:
        return {cls.key: hash_type}
