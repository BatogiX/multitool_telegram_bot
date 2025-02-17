from pydantic.dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class DecryptedRecord:
    service: str
    login: str
    password: str
