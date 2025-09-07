from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from config.db import ExpireT


class AbstractNoSQLDriver(ABC):
    @abstractmethod
    def get(self, transaction: object, name: str, path: str) -> str | None:
        pass

    @abstractmethod
    def set(self, transaction: object, name: str, path: str, value: str | int, expire: ExpireT) -> bool:
        pass

    @abstractmethod
    def delete(self, transaction: object, name: str, path: str) -> int:
        pass

    @abstractmethod
    async def connect(self) -> None:
        pass

    @abstractmethod
    async def close(self) -> None:
        pass

    @abstractmethod
    def create_transaction(self) -> object:
        pass

    @abstractmethod
    async def execute_transaction(self, transaction: object) -> list[Any]:
        pass
