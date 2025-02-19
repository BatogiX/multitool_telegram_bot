from pydantic import Field, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict


class KeyValueDatabaseConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="KEY_VALUE_DB_", frozen=True)

    host: str = "localhost"
    port: int = 6379
    username: str = ""
    password: str = ""
    url: str = "redis://localhost:6379"

    max_pool_size: int = 10


class RelationalDatabaseConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RELATIONAL_DB_", frozen=True)

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

    min_pool_size: int = 1
    max_pool_size: int = 10
    max_queries: int = 1000
