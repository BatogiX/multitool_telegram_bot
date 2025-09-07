from __future__ import annotations

import logging
from typing import Any, final, override

from aiogram.fsm.storage.memory import MemoryStorage

from .base import AbstractNoSQLDriver

logger = logging.getLogger(__name__)


@final
class MemoryStorageDriver(AbstractNoSQLDriver):
    """
    Implementation of a key-value Memory store.
    """

    def __init__(self) -> None:
        self.storage = MemoryStorage()

    async def connect(self) -> None:
        logger.info("Using MemoryStorage")

    async def close(self) -> None:
        await self.storage.close()
        logger.info("MemoryStorage has been closed")

    @override
    async def _set(self, key: str, value: Any, expire: int | None = None) -> None:
        pass

    async def _get_from_data(self, key: str) -> Any | None:
        pass
