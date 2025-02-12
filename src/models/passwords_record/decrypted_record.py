from pydantic.dataclasses import dataclass

@dataclass(frozen=True, kw_only=True)
class DecryptedRecord:
    login: str
    password: str
