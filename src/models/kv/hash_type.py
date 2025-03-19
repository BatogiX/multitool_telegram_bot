from typing import Dict


class HashType:
    key: str = "hash_type"

    def __new__(cls, hash_type: str) -> Dict[str, str]:
        return {cls.key: hash_type}
