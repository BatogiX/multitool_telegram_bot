from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, Self, cast, overload

from database.nosqlalchemy.base import JsonField

if TYPE_CHECKING:
    from types import TracebackType

    from aiogram.fsm.storage.base import StorageKey

    from config.db import ExpireT
    from database.nosqlalchemy.base import SimpleField

    from .engine import AsyncEngine


class AsyncSession:
    def __init__(self, engine: AsyncEngine, transaction: object, storage_key: StorageKey) -> None:
        self.engine = engine
        self.transaction = transaction
        self.storage_key = storage_key

    @classmethod
    def begin(cls, engine: AsyncEngine, storage_key: StorageKey) -> AsyncSession:
        trans = engine.driver.create_transaction()
        return cls(engine, trans, storage_key)

    def build_key(self, suffix: str, *, separator: str = ":") -> str:
        parts = [str(self.storage_key.bot_id), str(self.storage_key.chat_id), str(self.storage_key.user_id), suffix]
        return separator.join(parts)

    def resolve_field(self, field: object) -> tuple[str, str]:
        field = cast("SimpleField | JsonField", field)
        path = ""
        if isinstance(field, JsonField):
            name = self.build_key(field.suffix)
            path = field.key
        else:  # elif isinstance(field, SimpleField):
            name = self.build_key(field.key)
        return name, path

    def get(self, field: object) -> str | None:
        name, path = self.resolve_field(field)
        return self.engine.driver.get(self.transaction, name, path)

    @overload
    def set[T: str](self, field: T, value: T, expire: ExpireT) -> bool: ...
    @overload
    def set[T: int](self, field: T, value: T, expire: ExpireT) -> bool: ...
    def set(self, field: Any, value: Any, expire: Any) -> Any:
        name, path = self.resolve_field(field)
        return self.engine.driver.set(self.transaction, name, path, value, expire)

    def delete(self, field: object) -> int:
        name, path = self.resolve_field(field)
        return self.engine.driver.delete(self.transaction, name, path)

    async def close(self) -> None:
        pass

    async def commit(self) -> list[Any]:
        return await self.engine.driver.execute_transaction(self.transaction)

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self, typ: type[BaseException] | None, exc: BaseException | None, tb: TracebackType | None
    ) -> None:
        task = asyncio.create_task(self.close())
        await asyncio.shield(task)
