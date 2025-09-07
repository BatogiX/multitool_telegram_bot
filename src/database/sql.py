from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, ClassVar, Concatenate, final, override

from sqlalchemy.ext.asyncio import (
    AsyncSession,  # AsyncSession from sqlalchemy for .execute method that isn't deprecated
    async_sessionmaker,
    create_async_engine,
)
from sqlmodel import SQLModel, col, delete, desc, func, select, update

from config import BOT_CFG, SQL_DB_CFG
from models.sql import Password, User
from utils import fields, gen_salt

from .base import AbstractSQLDatabase

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence
    from types import CoroutineType

    from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

logger = logging.getLogger(__name__)


@final
class SQLDatabase(AbstractSQLDatabase):
    engine: ClassVar[AsyncEngine] = create_async_engine(SQL_DB_CFG.url, echo=True)
    Session: ClassVar[async_sessionmaker[AsyncSession]] = async_sessionmaker(engine)

    @override
    async def connect(self) -> None:
        async with self.engine.begin() as conn:
            logger.info("%s - Connected", self.engine.url.drivername)
            await self._create_tables(conn)

    @override
    async def close(self) -> None:
        logger.info("%s - Disconnected", self.engine.url.drivername)
        await self.engine.dispose(close=True)

    @staticmethod
    def with_session[**P, R](
        fn: Callable[Concatenate[AsyncSession, P], CoroutineType[Any, Any, R]],
    ) -> Callable[P, Callable[[AsyncSession], CoroutineType[Any, Any, R]]]:
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Callable[[AsyncSession], CoroutineType[Any, Any, R]]:
            def inner(session: AsyncSession) -> CoroutineType[Any, Any, R]:
                return fn(session, *args, **kwargs)

            return inner

        return wrapper

    @with_session
    @staticmethod
    async def create_user_if_not_exists(
        session: AsyncSession,
        user_id: int,
        user_name: str | None,
        user_full_name: str,
        /,
    ) -> bool:
        """Create a new user in the database."""
        existing_user = await session.get(User, user_id)
        if not existing_user:
            new_user = User(
                id=user_id,
                name=user_name,
                full_name=user_full_name,
                salt=gen_salt(),
            )
            session.add(new_user)
            return False
        return True


    @with_session
    @staticmethod
    async def get_services(
        session: AsyncSession,
        user_id: int,
        offset: int,
        /,
        *,
        limit: int = BOT_CFG.dynamic_buttons_limit,
    ) -> Sequence[str]:
        """Get all services for a user."""
        stmt = (
            select(Password.service)
            .where(
                Password.user_id == user_id,
                func.row_number().over(partition_by=Password.service, order_by=desc(Password.id)) == 1,
            )
            .order_by(desc(Password.id))
            .offset(offset * limit)
            .limit(limit)
        )

        return (await session.scalars(stmt)).all()

    @with_session
    @staticmethod
    async def add_password(
        session: AsyncSession,
        user_id: int,
        service: str,
        ciphertext: bytes,
        /,
    ) -> None:
        """Create a new service for a user."""
        session.add(Password(user_id=user_id, service=service, ciphertext=ciphertext))

    @with_session
    @staticmethod
    async def get_passwords_by_service(
        session: AsyncSession,
        user_id: int,
        service: str,
        offset: int,
        /,
        *,
        limit: int = BOT_CFG.dynamic_buttons_limit,
    ) -> Sequence[Password]:
        """Get all passwords of service for a user."""
        stmt = (
            select(Password)
            .where(Password.user_id == user_id, Password.service == service)
            .offset(offset * limit)
            .limit(limit + 1)
        )

        return (await session.scalars(stmt)).all()

    @with_session
    @staticmethod
    async def get_rand_password(session: AsyncSession, user_id: int, /) -> Password | None:
        """Get a random passwords record for a user."""
        return await session.get(Password, user_id)

    @with_session
    @staticmethod
    async def change_service(
        session: AsyncSession,
        new_service: str,
        user_id: int,
        old_service: str,
        /,
    ) -> None:
        """Change service name for a user."""
        stmt = (
            update(Password)
            .where(col(Password.user_id) == user_id, col(Password.service) == old_service)
            .values({fields(Password).service: new_service})
        )

        await session.execute(stmt)

    @with_session
    @staticmethod
    async def delete_passwords(
        session: AsyncSession,
        user_id: int,
        /,
    ) -> None:
        """Delete all services for a user."""
        stmt = delete(Password).where(col(Password.user_id) == user_id)
        await session.execute(stmt)

    @with_session
    @staticmethod
    async def delete_passwords_by_service(
        session: AsyncSession,
        user_id: int,
        service: str,
        /,
    ) -> None:
        """Delete a service for a user."""
        stmt = delete(Password).where(
            col(Password.user_id) == user_id,
            col(Password.service) == service,
        )
        await session.execute(stmt)

    @with_session
    @staticmethod
    async def delete_password(
        session: AsyncSession,
        user_id: int,
        service: str,
        ciphertext: str,
        /,
    ) -> None:
        """Delete a password for a user."""
        stmt = delete(Password).where(
            col(Password.user_id) == user_id,
            col(Password.service) == service,
            col(Password.ciphertext) == ciphertext,
        )
        await session.execute(stmt)

    @with_session
    @staticmethod
    async def update_credentials(
        session: AsyncSession,
        user_id: int,
        service: str,
        current_ciphertext: str,
        new_ciphertext: str,
        /,
    ) -> None:
        """Updates login and/or password for record"""
        stmt = (
            update(Password)
            .where(
                col(Password.user_id) == user_id,
                col(Password.service) == service,
                col(Password.ciphertext) == current_ciphertext,
            )
            .values({fields(Password).ciphertext: new_ciphertext})
        )

        await session.execute(stmt)

    @with_session
    @staticmethod
    async def import_passwords(
        session: AsyncSession,
        user_id: int,
        records: list[Password],
        /,
    ) -> None:
        """Import passwords for a user."""
        pass

    @with_session
    @staticmethod
    async def export_passwords(
        session: AsyncSession,
        user_id: int,
        /,
    ) -> Sequence[Password]:
        """Import passwords for a user."""
        stmt = select(Password).where(Password.user_id == user_id)
        result = await session.scalars(stmt)
        return result.all()

    @with_session
    @staticmethod
    async def inline_search_service(
        session: AsyncSession,
        user_id: int,
        service: str,
        /,
        *,
        limit: int = BOT_CFG.dynamic_buttons_limit,
    ) -> Sequence[str]:
        """Search for passwords of service for a user."""
        stmt = (
            select(Password.service)
            .distinct()
            .where(
                Password.user_id == user_id,
                col(Password.service).like(service),
            )
            .limit(limit)
        )

        return (await session.scalars(stmt)).all()

    @with_session
    @staticmethod
    async def get_salt(
        session: AsyncSession,
        user_id: int,
        /,
    ) -> bytes:
        user = await session.get(User, user_id)
        if not user:
            msg = f"User {user_id} has no salt"
            raise ValueError(msg)

        return user.salt

    @staticmethod
    async def _create_tables(conn: AsyncConnection) -> None:
        """Initialize database."""
        await conn.run_sync(SQLModel.metadata.create_all)


async def test():
    sql = SQLDatabase()
    a, b = await sql.execute(sql.get_rand_password(123), sql.get_salt(213123))
    print(a, b)
