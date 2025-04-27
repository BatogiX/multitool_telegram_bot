import logging
from typing import Optional, Any

from aiogram.fsm.storage.memory import MemoryStorage

from database.base import AbstractKeyValueDatabase


class MemoryStorageManager(AbstractKeyValueDatabase):
    """
    Implementation of a key–value Memory store.
    """

    def __init__(self) -> None:
        self.storage = MemoryStorage()

    async def connect(self) -> None:
        logging.info("Using MemoryStorage")

    async def close(self) -> None:
        await self.storage.close()
        logging.info("MemoryStorage has been closed")

    async def _set(self, key: str, value: Any, expire: Optional[int] = None):
        pass

    async def _get_from_data(self, key: str) -> Optional[Any]:
        pass
