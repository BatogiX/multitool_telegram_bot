from typing import Dict


class PasswordManagerPasswordsOffset:
    key: str = "pm_pwd_offset"

    def __new__(cls, offset: int) -> Dict[str, int]:
        return {cls.key: offset}
