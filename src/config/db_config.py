from typing import Literal, Optional

from pydantic import Field, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict


class KeyValueDatabaseConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="KEY_VALUE_DB_", frozen=True)

    backend: Literal["redis", "memory"] = Field(default="redis", validate_default=True)

    host: str = "localhost"
    port: int = 6379
    username: str = ""
    password: str = ""
    url: str = "redis://localhost:6379"

    max_pool_size: int = Field(default=10, ge=1)
    state_ttl: Optional[int] = Field(default=None, ge=1)
    data_ttl: Optional[int] = Field(default=None, ge=1)


class RelationalDatabaseConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RELATIONAL_DB_", frozen=True)

    backend: Literal["postgres"] = Field(default="postgres", validate_default=True)

    host: str = "localhost"
    port: int = 5432
    user: str = ""
    password: str = ""
    name: str = ""
    url: str = Field(
        default="",
        validation_alias=AliasChoices(
            "DATABASE_URL",
            model_config.get("env_prefix") + "URL"
        )
    )

    min_pool_size: int = Field(default=1, ge=1)
    max_pool_size: int = Field(default=10, ge=1)
    max_queries: int = Field(default=1000, ge=1)
