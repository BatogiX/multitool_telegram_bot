from pydantic_settings import BaseSettings, SettingsConfigDict


class Argon2Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        env_prefix="ARGON2_",
        extra="allow",
    )

    TIME_COST: int = 3
    MEMORY_COST: int = 128 * 1024  # 128 MiB
    PARALLELISM: int = 4
    HASH_LEN: int = 32


class PasswordManagerConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        env_prefix="PM_CONFIG_",
        extra="allow",
    )

    GCM_IV_SIZE: int = 12  # Recommended IV size for AES-GCM
    SALT_LEN: int = 16
    ARGON2: Argon2Config = Argon2Config()

pm_config = PasswordManagerConfig()
