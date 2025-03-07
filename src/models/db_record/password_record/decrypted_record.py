from pydantic import BaseModel, ConfigDict


class DecryptedRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    service: str
    login: str
    password: str
