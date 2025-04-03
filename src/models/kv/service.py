from typing import Dict


class Service:
    key = "service"

    def __new__(cls, service_name: str) -> Dict[str, str]:
        return {cls.key: service_name}
