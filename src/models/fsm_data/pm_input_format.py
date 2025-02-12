class PasswordManagerInputFormat:
    key: str = "pm_input_format"

    def __new__(cls, text: str):
        return {cls.key: text}
