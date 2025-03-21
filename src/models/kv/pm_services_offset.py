from typing import Dict


class PasswordManagerServicesOffset:
    key: str = "pm_services_offset"

    def __new__(cls, offset: int) -> Dict[str, int]:
        return {cls.key: offset}
