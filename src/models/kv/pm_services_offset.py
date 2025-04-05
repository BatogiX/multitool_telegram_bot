from typing import Dict

from models.kv import BaseKeyValue


class PasswordManagerServicesOffset(BaseKeyValue):
    key = "pm_services_offset"

    def __new__(cls, offset: int) -> Dict[str, int]:
        return {cls.key: offset}
