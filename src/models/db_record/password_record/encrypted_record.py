from pydantic.dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class EncryptedRecord:
    service: str
    iv: bytes
    tag: bytes
    ciphertext: bytes
