from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar, overload

from config import NOSQL_DB_CFG
from database.nosqlalchemy.engine import create_async_engine

if TYPE_CHECKING:
    from collections.abc import Callable
    from types import CoroutineType

    import nosqlalchemy.session as nosqlalchemy
    import sqlalchemy.ext.asyncio as sqlalchemy
    from aiogram.fsm.storage.base import BaseStorage, StorageKey
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

    from config.db import ExpireT


class AbstractDatabase(ABC):
    """Base abstract class for all DBs."""

    @abstractmethod
    async def connect(self) -> None:
        """Method for establishing a connection to the database."""

    @abstractmethod
    async def close(self) -> None:
        """Method for closing a connection."""


class AbstractSQLDatabase(AbstractDatabase):
    engine: ClassVar[sqlalchemy.AsyncEngine]
    Session: ClassVar[async_sessionmaker[AsyncSession]]

    @overload
    async def execute[T1](
        self,
        func1: Callable[[sqlalchemy.AsyncSession], CoroutineType[Any, Any, T1]],
        /,
    ) -> T1: ...
    @overload
    async def execute[T1, T2](
        self,
        func1: Callable[[sqlalchemy.AsyncSession], CoroutineType[Any, Any, T1]],
        func2: Callable[[sqlalchemy.AsyncSession], CoroutineType[Any, Any, T2]],
        /,
    ) -> tuple[T1, T2]: ...
    @overload
    async def execute[T1, T2, T3](
        self,
        func1: Callable[[sqlalchemy.AsyncSession], CoroutineType[Any, Any, T1]],
        func2: Callable[[sqlalchemy.AsyncSession], CoroutineType[Any, Any, T2]],
        func3: Callable[[sqlalchemy.AsyncSession], CoroutineType[Any, Any, T3]],
        /,
    ) -> tuple[T1, T2, T3]: ...
    @overload
    async def execute[T1, T2, T3, T4](
        self,
        func1: Callable[[sqlalchemy.AsyncSession], CoroutineType[Any, Any, T1]],
        func2: Callable[[sqlalchemy.AsyncSession], CoroutineType[Any, Any, T2]],
        func3: Callable[[sqlalchemy.AsyncSession], CoroutineType[Any, Any, T3]],
        func4: Callable[[sqlalchemy.AsyncSession], CoroutineType[Any, Any, T4]],
        /,
    ) -> tuple[T1, T2, T3, T4]: ...
    @overload
    async def execute[T1, T2, T3, T4, T5](
        self,
        func1: Callable[[sqlalchemy.AsyncSession], CoroutineType[Any, Any, T1]],
        func2: Callable[[sqlalchemy.AsyncSession], CoroutineType[Any, Any, T2]],
        func3: Callable[[sqlalchemy.AsyncSession], CoroutineType[Any, Any, T3]],
        func4: Callable[[sqlalchemy.AsyncSession], CoroutineType[Any, Any, T4]],
        func5: Callable[[sqlalchemy.AsyncSession], CoroutineType[Any, Any, T5]],
        /,
    ) -> tuple[T1, T2, T3, T4, T5]: ...
    @overload
    async def execute[T1, T2, T3, T4, T5, T6](
        self,
        func1: Callable[[sqlalchemy.AsyncSession], CoroutineType[Any, Any, T1]],
        func2: Callable[[sqlalchemy.AsyncSession], CoroutineType[Any, Any, T2]],
        func3: Callable[[sqlalchemy.AsyncSession], CoroutineType[Any, Any, T3]],
        func4: Callable[[sqlalchemy.AsyncSession], CoroutineType[Any, Any, T4]],
        func5: Callable[[sqlalchemy.AsyncSession], CoroutineType[Any, Any, T5]],
        func6: Callable[[sqlalchemy.AsyncSession], CoroutineType[Any, Any, T6]],
        /,
    ) -> tuple[T1, T2, T3, T4, T5, T6]: ...
    async def execute(self, *funcs: Any) -> Any:
        async with self.Session() as session:
            tasks = [func(session) for func in funcs]
            results = await asyncio.gather(*tasks)
            await session.commit()
        return results


class AbstractNoSQLDatabase(AbstractDatabase):
    """Abstract class for key-value storage (Redis, Memcached)."""

    engine: ClassVar[nosqlalchemy.AsyncEngine] = create_async_engine(NOSQL_DB_CFG.nosqlalchemy_url)
    storage: BaseStorage
    state_ttl: ClassVar[ExpireT] = NOSQL_DB_CFG.state_ttl
    data_ttl: ClassVar[ExpireT] = NOSQL_DB_CFG.data_ttl

    @overload
    async def execute[T1](
        self,
        func1: Callable[[nosqlalchemy.AsyncSession], T1],
        /,
        *,
        storage_key: StorageKey,
    ) -> T1: ...
    @overload
    async def execute[T1, T2](
        self,
        func1: Callable[[nosqlalchemy.AsyncSession], T1],
        func2: Callable[[nosqlalchemy.AsyncSession], T2],
        /,
        *,
        storage_key: StorageKey,
    ) -> tuple[T1, T2]: ...
    @overload
    async def execute[T1, T2, T3](
        self,
        func1: Callable[[nosqlalchemy.AsyncSession], T1],
        func2: Callable[[nosqlalchemy.AsyncSession], T2],
        func3: Callable[[nosqlalchemy.AsyncSession], T3],
        /,
        *,
        storage_key: StorageKey,
    ) -> tuple[T1, T2, T3]: ...
    @overload
    async def execute[T1, T2, T3, T4](
        self,
        func1: Callable[[nosqlalchemy.AsyncSession], T1],
        func2: Callable[[nosqlalchemy.AsyncSession], T2],
        func3: Callable[[nosqlalchemy.AsyncSession], T3],
        func4: Callable[[nosqlalchemy.AsyncSession], T4],
        /,
        *,
        storage_key: StorageKey,
    ) -> tuple[T1, T2, T3, T4]: ...
    @overload
    async def execute[T1, T2, T3, T4, T5](
        self,
        func1: Callable[[nosqlalchemy.AsyncSession], T1],
        func2: Callable[[nosqlalchemy.AsyncSession], T2],
        func3: Callable[[nosqlalchemy.AsyncSession], T3],
        func4: Callable[[nosqlalchemy.AsyncSession], T4],
        func5: Callable[[nosqlalchemy.AsyncSession], T5],
        /,
        *,
        storage_key: StorageKey,
    ) -> tuple[T1, T2, T3, T4, T5]: ...
    @overload
    async def execute[T1, T2, T3, T4, T5, T6](
        self,
        func1: Callable[[nosqlalchemy.AsyncSession], T1],
        func2: Callable[[nosqlalchemy.AsyncSession], T2],
        func3: Callable[[nosqlalchemy.AsyncSession], T3],
        func4: Callable[[nosqlalchemy.AsyncSession], T4],
        func5: Callable[[nosqlalchemy.AsyncSession], T5],
        func6: Callable[[nosqlalchemy.AsyncSession], T6],
        /,
        *,
        storage_key: StorageKey,
    ) -> tuple[T1, T2, T3, T4, T5, T6]: ...
    async def execute(self, *funcs: Any, storage_key: Any) -> Any:
        transaction = self.engine.begin(storage_key)
        for func in funcs:
            func(transaction)
        return await transaction.commit()
