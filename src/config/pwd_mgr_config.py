from pydantic_settings import BaseSettings, SettingsConfigDict


class Argon2Config(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ARGON2_", frozen=True)

    TIME_COST: int = 3
    MEMORY_COST: int = 128 * 1024  # 128 MiB
    PARALLELISM: int = 4
    HASH_LEN: int = 32  # 256-bit


class PasswordManagerConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PWD_MAN_", frozen=True)

    GCM_IV_SIZE: int = 12  # 96-bit Recommended IV size for AES-GCM
    SALT_LEN: int = 16  # 128-bit
    ARGON2: Argon2Config = Argon2Config()
