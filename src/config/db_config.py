from typing import Optional

from pydantic import Field, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict

from db import DatabaseManager
from db.postgresql import PostgresqlManager
from db.redis import RedisManager


# ==================== #
# 🔥 DATABASE SETTINGS #
# ==================== #

class KeyValueDatabaseConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        env_prefix="KEY_VALUE_DB_",
        extra="allow",
    )

    host: str = "localhost"
    port: int = 6379
    username: Optional[str] = None
    password: Optional[str] = None
    url: Optional[str] = None

    max_pool_size: int = 10


class RelationalDatabaseConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        env_prefix="RELATIONAL_DB_",
        extra="allow"
    )

    host: str = "localhost"
    name: str = "database"
    user: str = "user"
    port: int = 5432
    password: Optional[str] = None
    url: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "DATABASE_URL",
            model_config.get("env_prefix") + "URL"
        )
    )

    min_pool_size: int = 1
    max_pool_size: int = 10
    max_queries: int = 1000


# ================================= #
# 🧰 DATABASE MANAGER INSTANTIATION #
# ================================= #

db_manager: DatabaseManager = DatabaseManager(
    key_value_db=RedisManager(config=KeyValueDatabaseConfig()),
    relational_db=PostgresqlManager(config=RelationalDatabaseConfig())
)
