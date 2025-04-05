from typing import Dict

from models.kv import BaseKeyValue


class Service(BaseKeyValue):
    key = "service"

    def __new__(cls, service_name: str) -> Dict[str, str]:
        return {cls.key: service_name}
