from typing import Dict


class PasswordManagerInputFormat:
    key = "pm_input_format"

    def __new__(cls, text: str) -> Dict[str, str]:
        return {cls.key: text}
