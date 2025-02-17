from pydantic.dataclasses import dataclass

from models.db_record.password_record import EncryptedRecord


@dataclass(frozen=True, kw_only=True)
class PasswordRecord:
    service: str
    encrypted_record: EncryptedRecord