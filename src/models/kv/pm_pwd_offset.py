from typing import Dict


class PasswordManagerPasswordsOffset:
    key: str = "pm_pwd_offset_data"

    def __new__(cls, offset: int) -> Dict[str, int]:
        return {cls.key: offset}
