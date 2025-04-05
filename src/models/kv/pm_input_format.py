from typing import Dict

from models.kv import BaseKeyValue


class PasswordManagerInputFormat(BaseKeyValue):
    key = "pm_input_format"

    def __new__(cls, text: str) -> Dict[str, str]:
        return {cls.key: text}
