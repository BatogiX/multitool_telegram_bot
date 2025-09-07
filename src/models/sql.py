from __future__ import annotations

from datetime import UTC, datetime
from typing import final

from sqlmodel import Column, Field, LargeBinary, SQLModel


@final
class User(SQLModel, table=True):
    id: int = Field(primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    name: str | None
    full_name: str
    salt: bytes = Field(sa_column=Column(LargeBinary))


class PasswordModel(SQLModel):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", ondelete="CASCADE")
    service: str


@final
class Password(PasswordModel, table=True):
    ciphertext: bytes = Field(sa_column=Column(LargeBinary))


@final
class DecryptedPassword(PasswordModel):
    login: str
    password: str
