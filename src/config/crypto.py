from typing import ClassVar, Final, final

from argon2 import (
    DEFAULT_HASH_LENGTH,
    DEFAULT_MEMORY_COST,
    DEFAULT_PARALLELISM,
    DEFAULT_RANDOM_SALT_LENGTH,
    DEFAULT_TIME_COST,
    Type,
)
from pydantic import Field
from pydantic_settings import BaseSettings

from utils.config import base_settings_config


@final
class CryptographyConfig(BaseSettings):
    PREFIX: ClassVar[str] = "CRYPTO_"
    model_config = base_settings_config(prefix=PREFIX)

    pepper: bytes = Field(default=...)  # os.urandom(32).hex()
    nonce_length: int = Field(default=16, ge=16)  # 16 bytes
    salt_length: int = Field(default=32, ge=16)  # 32 bytes

    # Argon2 parameters
    argon2_hash_length: int = Field(default=DEFAULT_HASH_LENGTH, ge=32)  # 32 bytes
    argon2_memory_cost: int = Field(default=DEFAULT_MEMORY_COST, ge=65536)  # 64 MiB
    argon2_parallelism: int = Field(default=DEFAULT_PARALLELISM, ge=1)  # 4
    argon2_salt_length: int = Field(default=DEFAULT_RANDOM_SALT_LENGTH, ge=1)  # 16 bytes
    argon2_time_cost: int = Field(default=DEFAULT_TIME_COST, ge=1)  # 3
    argon2_type: Type = Type.ID  # Argon2id


CRYPTO_CFG: Final[CryptographyConfig] = CryptographyConfig()
