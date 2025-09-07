from __future__ import annotations

from typing import final

from database.nosqlalchemy.base import JsonSchema, Schema


@final
class User(Schema):
    state: str
    cache_user_created: int


@final
class Data(JsonSchema):
    offset_service: int
    service: str
    offset_password: int
    message_id: int
    input_format: str
    hash_type: str
