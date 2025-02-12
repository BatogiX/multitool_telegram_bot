from pydantic import BaseModel


class Argon2Config(BaseModel):
    TIME_COST: int = 3
    MEMORY_COST: int = 128 * 1024  # 128 MiB
    PARALLELISM: int = 4
    HASH_LEN: int = 32


class PasswordManagerConfig(BaseModel):
    GCM_IV_SIZE: int = 12  # Recommended IV size for AES-GCM
    SALT_LEN: int = 16
    ARGON2: Argon2Config = Argon2Config()


pm_config = PasswordManagerConfig()
