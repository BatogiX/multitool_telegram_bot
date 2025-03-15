import logging
from typing import Optional

from aiogram.fsm.storage.memory import MemoryStorage


from database.base import AbstractKeyValueDatabase


class MemoryStorageManager(AbstractKeyValueDatabase):
    """
    Implementation of a key–value store for Redis.
    """
    _storage = Optional[MemoryStorage] = None

    async def connect(self) -> MemoryStorage:
        """
        Connect to Redis using URL if provided, otherwise use host and port.
        """
        if self._storage is None:
            self._storage = MemoryStorage()
            logging.info(f"Using MemoryStorage")
        return self._storage

    async def close(self) -> None:
        """
        Close from MemoryStorage.
        """
        if self._storage:
            await self._storage.close()
            logging.info("MemoryStorage has been closed")
            self._storage = None

    async def get_data(self, key: str):
        key = self.build_key()
        return await self._storage.get_data(key)

    async def set(self, key: str, value: str, expire: int = None):
        await self._storage.set_data(key, value)

    async def delete(self, key: str):
        await self._storage.delete(key)


