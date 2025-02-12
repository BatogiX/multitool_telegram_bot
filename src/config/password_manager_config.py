# ====================== #
# PASSWORD HASH SETTINGS #
# ====================== #

class Argon2Config:
    TIME_COST = 3
    MEMORY_COST = 128 * 1024  # 128 MiB
    PARALLELISM = 4
    HASH_LEN = 32


class PasswordManagerConfig:
    GCM_IV_SIZE = 12  # Recommended IV size for AES-GCM
    SALT_LEN = 16
    ARGON2 = Argon2Config
