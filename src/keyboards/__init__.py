from .inline_keyboards import InlineKeyboards
from .reply_keyboards import ReplyKeyboards


class Keyboards:
    inline = InlineKeyboards
    reply = ReplyKeyboards


__all__ = "InlineKeyboards"
