from __future__ import annotations

from typing import TYPE_CHECKING, Any, LiteralString, Self

from pydantic_core import PydanticCustomError

if TYPE_CHECKING:
    from types import CoroutineType

    from config.db import NOSQL_DIALECT, SQL_DIALECT


class UnknownMethodError(Exception):
    """Raised when a coroutine is called with an unknown method."""

    def __init__[T](self, coro: CoroutineType[Any, Any, T]) -> None:
        message = f"Unknown method in coroutine {coro}"
        super().__init__(message)


class InvalidNoSQLDialectError(Exception):
    def __init__(self, dialect: str, valid_dialects: tuple[NOSQL_DIALECT, ...]) -> None:
        msg = f"Unsupported NoSQL dialect: {dialect}. Valid options: {valid_dialects}"
        super().__init__(msg)


class InvalidSQLDialectError(Exception):
    def __init__(self, dialect: str, valid_dialects: tuple[SQL_DIALECT, ...]) -> None:
        msg = f"Unsupported SQL dialect: {dialect}. Valid options: {valid_dialects}"
        super().__init__(msg)


class InvalidSQLAlchemyUrlError(ValueError):
    def __init__(self, value: str) -> None:
        error_type = "url_no_driver"
        message_template = "SQLAlchemy URL must include driver specification (e.g., postgresql+asyncpg://...)"
        context = {"input": value, "expected_format": "dialect+driver://..."}
        msg = f"{message_template} [type={error_type}, context={context}]"
        super().__init__(msg)
