from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Concatenate, cast, final, override

from models.nosql import Data, User

from .base import AbstractNoSQLDatabase

if TYPE_CHECKING:
    from collections.abc import Callable

    from aiogram.fsm.context import FSMContext

    from .nosqlalchemy.session import AsyncSession

logger = logging.getLogger(__name__)


@final
class NoSQLDatabase(AbstractNoSQLDatabase):
    @override
    async def connect(self) -> None:
        await self.engine.connect()
        logger.info("%s - Connected", self.engine.url)

    @override
    async def close(self) -> None:
        await self.engine.close()
        logger.info("%s - Disconnected", self.engine.url)

    @staticmethod
    def with_session[**P, R](
        fn: Callable[Concatenate[type[NoSQLDatabase], AsyncSession, P], R],
    ) -> Callable[Concatenate[type[NoSQLDatabase], P], Callable[[AsyncSession], R]]:
        def wrapper(cls: type[NoSQLDatabase], *args: P.args, **kwargs: P.kwargs) -> Callable[[AsyncSession], R]:
            def inner(session: AsyncSession) -> R:
                return fn(cls, session, *args, **kwargs)

            return inner

        return wrapper

    @with_session
    @classmethod
    def set_state(cls, session: AsyncSession, state_value: str) -> bool:
        session.set(User.state, state_value, cls.state_ttl)
        return cast("bool", None)

    @with_session
    @classmethod
    def set_message_id_to_delete(cls, session: AsyncSession, msg_id: int) -> bool:
        session.set(Data.message_id, msg_id, cls.data_ttl)
        return cast("bool", None)

    @with_session
    @classmethod
    def set_service(cls, session: AsyncSession, service_name: str) -> bool:
        session.set(Data.service, service_name, cls.data_ttl)
        return cast("bool", None)

    @with_session
    @classmethod
    def set_hash_type(cls, session: AsyncSession, hash_type: str) -> bool:
        session.set(Data.hash_type, hash_type, cls.data_ttl)
        return cast("bool", None)

    @with_session
    @classmethod
    def set_input_format_text(cls, session: AsyncSession, text: str) -> bool:
        session.set(Data.input_format, text, cls.data_ttl)
        return cast("bool", None)

    @with_session
    @classmethod
    def set_pwds_offset(cls, session: AsyncSession, offset: int) -> bool:
        session.set(Data.offset_password, offset, cls.data_ttl)
        return cast("bool", None)

    @with_session
    @classmethod
    def set_services_offset(cls, session: AsyncSession, offset: int) -> bool:
        session.set(Data.offset_service, offset, cls.data_ttl)
        return cast("bool", None)

    @with_session
    @classmethod
    def set_cache_user_created(cls, session: AsyncSession) -> bool:
        session.set(User.cache_user_created, 1, 86400)
        return cast("bool", None)

    @with_session
    @classmethod
    def get_state(cls, session: AsyncSession) -> str | None:
        session.get(User.state)
        return cast("str | None", None)

    @with_session
    @classmethod
    def get_message_id_to_delete(cls, session: AsyncSession) -> int | None:
        session.get(Data.message_id)
        return cast("int | None", None)

    @with_session
    @classmethod
    def get_service(cls, session: AsyncSession) -> str | None:
        session.get(Data.service)
        return cast("str | None", None)

    @with_session
    @classmethod
    def get_hash_type(cls, session: AsyncSession) -> str | None:
        session.get(Data.hash_type)
        return cast("str | None", None)

    @with_session
    @classmethod
    def get_input_format_text(cls, session: AsyncSession) -> str | None:
        session.get(Data.input_format)
        return cast("str | None", None)

    @with_session
    @classmethod
    def get_pwds_offset(cls, session: AsyncSession) -> int | None:
        session.get(Data.offset_password)
        return cast("int | None", None)

    @with_session
    @classmethod
    def get_services_offset(cls, session: AsyncSession) -> int | None:
        session.get(Data.offset_service)
        return cast("int | None", None)

    @with_session
    @classmethod
    def get_cache_user_created(cls, session: AsyncSession) -> str | None:
        session.get(User.cache_user_created)
        return cast("str | None", None)

    @with_session
    @classmethod
    def clear_state(cls, session: AsyncSession) -> int:
        session.delete(User.state)
        return cast("int", None)


async def test() -> None:
    nosql = NoSQLDatabase()
    state = cast("FSMContext", None)
    a, b = await nosql.execute(nosql.get_message_id_to_delete(), nosql.get_hash_type(), storage_key=state.key)
    print(a, b)
