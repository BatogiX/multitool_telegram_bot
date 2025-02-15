class PasswordManagerServicesOffset:
    key: str = "pm_services_offset"

    def __new__(cls, offset: int):
        return {cls.key: offset}
