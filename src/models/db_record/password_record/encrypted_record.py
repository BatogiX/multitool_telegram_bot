from pydantic import BaseModel, ConfigDict


class EncryptedRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    service: str
    iv: bytes
    tag: bytes
    ciphertext: bytes
