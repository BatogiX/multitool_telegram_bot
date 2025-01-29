from aiogram import Router
from aiogram.types import Message

message_router = Router(name=__name__)


@message_router.message()
async def pass_func(message: Message):
    pass
