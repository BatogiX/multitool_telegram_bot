from typing import Dict


class PasswordManagerInputFormat:
    key: str = "pm_input_format"

    def __new__(cls, text: str) -> Dict[str, str]:
        return {cls.key: text}
