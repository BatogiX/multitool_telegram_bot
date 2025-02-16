from pydantic.dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class EncryptedRecord:
    iv: bytes
    tag: bytes
    ciphertext: bytes
