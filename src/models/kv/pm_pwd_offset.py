class PasswordManagerPasswordsOffset:
    key: str = "pm_pwd_offset"

    def __new__(cls, offset: int):
        return {cls.key: offset}
