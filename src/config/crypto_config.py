from pydantic_settings import BaseSettings, SettingsConfigDict
from argon2 import (
    DEFAULT_TIME_COST,
    DEFAULT_MEMORY_COST,
    DEFAULT_PARALLELISM,
    DEFAULT_HASH_LENGTH,
    DEFAULT_RANDOM_SALT_LENGTH,
    Type,
)


class CryptographyConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CRYPTO_", frozen=True)

    pepper: bytes = b""                                            # (Recommended 256-bit)
    random_nonce_length: int = 16                                  # 16 (128-bit)

    # Argon2 parameters
    argon2_time_cost: int = DEFAULT_TIME_COST                      # 3
    argon2_memory_cost: int = DEFAULT_MEMORY_COST                  # 65536 (64 MiB)
    argon2_parallelism: int = DEFAULT_PARALLELISM                  # 4
    argon2_hash_length: int = DEFAULT_HASH_LENGTH                  # 32 (256-bit)
    argon2_random_salt_length: int = DEFAULT_RANDOM_SALT_LENGTH    # 16 (128-bit)
    argon2_type: Type = Type.ID                                    # Argon2id


crypto_cfg: CryptographyConfig = CryptographyConfig()
