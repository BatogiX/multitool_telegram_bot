from __future__ import annotations

from typing import TYPE_CHECKING

from .session import AsyncSession

if TYPE_CHECKING:
    from aiogram.fsm.storage.base import StorageKey

    from .drivers.base import AbstractNoSQLDriver


class AsyncEngine:
    def __init__(self, driver: AbstractNoSQLDriver, url: str) -> None:
        self.driver = driver
        self.url = url

    async def connect(self) -> None:
        await self.driver.connect()

    async def close(self) -> None:
        await self.driver.close()

    def begin(self, storage_key: StorageKey) -> AsyncSession:
        return AsyncSession.begin(self, storage_key)


def create_async_engine(url: str) -> AsyncEngine:
    idx_colon = url.find(":")
    dialect = url[:idx_colon]

    if dialect == "redis":
        from .drivers.redis import RedisDriver  # noqa: PLC0415

        driver = RedisDriver()
    elif dialect == "mongodb":
        from .drivers.mongodb import MongoDriver  # noqa: PLC0415

        driver = MongoDriver()
    else:
        from .drivers.memory import MemoryStorageDriver  # noqa: PLC0415

        driver = MemoryStorageDriver()

    return AsyncEngine(driver, url)
