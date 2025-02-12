class HashType:
    key: str = "hash_type"

    def __new__(cls, hash_type: str):
        return {cls.key: hash_type}
