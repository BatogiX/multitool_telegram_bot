from datetime import timedelta
from typing import ClassVar, Final, Literal, final, get_args

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings
from sqlalchemy import URL, make_url

from exceptions import InvalidNoSQLDialectError, InvalidSQLAlchemyUrlError
from utils.config import base_settings_config

SQL_DIALECT = Literal["postgresql", "mysql", "oracle", "mssql", "sqlite"]
SQL_DRIVER = Literal["asyncpg", "asyncmy", "oracledb", "aioodbc", "aiosqlite"]

SQL_DIALECT_TO_DRIVER_DICT: dict[SQL_DIALECT, SQL_DRIVER] = dict(
    zip(get_args(SQL_DIALECT), get_args(SQL_DRIVER), strict=True)
)

NOSQL_DIALECT = Literal["redis", "mongodb", "memory"]
NOSQL_DRIVER = Literal["redis", "pymongo", "python"]

NOSQL_DIALECT_TO_DRIVER_DICT: dict[NOSQL_DIALECT, NOSQL_DRIVER] = dict(
    zip(get_args(NOSQL_DIALECT), get_args(NOSQL_DRIVER), strict=True)
)

ExpireT = int | timedelta | None


@final
class NoSQLDatabaseConfig(BaseSettings):
    PREFIX: ClassVar[str] = "DB_NOSQL_"
    model_config = base_settings_config(prefix=PREFIX)

    url: str = Field(default=...)

    max_pool_size: int = Field(default=10, ge=1)
    state_ttl: ExpireT = Field(default=None, ge=1)
    data_ttl: ExpireT = Field(default=None, ge=1)

    @property
    def dialect(self) -> NOSQL_DIALECT:
        idx = self.url.find(":")
        dialect = self.url[0:idx]
        valid_dialects: tuple[NOSQL_DIALECT, ...] = get_args(NOSQL_DIALECT)

        if dialect in valid_dialects:
            return dialect
        raise InvalidNoSQLDialectError(dialect, valid_dialects)

    @property
    def driver(self) -> NOSQL_DRIVER:
        return NOSQL_DIALECT_TO_DRIVER_DICT[self.dialect]

    @property
    def params(self) -> str:
        idx = self.url.find(":")
        return self.url[idx:]

    @property
    def nosqlalchemy_url(self) -> str:
        return f"{self.dialect}+{self.driver}{self.params}"


@final
class SQLDatabaseConfig(BaseSettings):
    PREFIX: ClassVar[str] = "DB_SQL_"
    model_config = base_settings_config(prefix=PREFIX)

    url: URL = Field(
        default=...,
        validation_alias=AliasChoices(
            PREFIX + "URL",
            "DATABASE_URL",
        ),
    )

    min_pool_size: int = Field(default=1, ge=1)
    max_pool_size: int = Field(default=10, ge=1)
    max_queries: int = Field(default=1000, ge=1)

    @field_validator("url", mode="before")
    @classmethod
    def is_sqlalchemy_url(cls, value: str) -> URL:
        if "+" not in value:
            raise InvalidSQLAlchemyUrlError(value)
        return make_url(value)


NOSQL_DB_CFG: Final[NoSQLDatabaseConfig] = NoSQLDatabaseConfig()
SQL_DB_CFG: Final[SQLDatabaseConfig] = SQLDatabaseConfig()
