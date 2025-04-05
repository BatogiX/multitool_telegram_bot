from abc import ABC, abstractmethod
from typing import Any


class BaseKeyValue(ABC):
    @staticmethod
    @abstractmethod
    def key(*args, **kwargs) -> str: ...

    @classmethod
    @abstractmethod
    def create(cls, *args, **kwargs) -> dict[str, Any]: ...
