from typing import Dict

from models.kv import BaseKeyValue


class PasswordManagerPasswordsOffset(BaseKeyValue):
    key = "pm_pwd_offset"

    def __new__(cls, offset: int) -> Dict[str, int]:
        return {cls.key: offset}
