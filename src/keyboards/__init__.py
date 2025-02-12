from .inline_keyboards import InlineHashMenuKeyboard, InlinePasswordManagerKeyboard, InlineStartMenuKeyboard
from .reply_keyboards import PassClass

__all__ = (
    'InlineKeyboards',
    'ReplyKeyboards'
)


class InlineKeyboards(InlineHashMenuKeyboard, InlineStartMenuKeyboard, InlinePasswordManagerKeyboard):
    __slots__ = ()


class ReplyKeyboards(PassClass):
    __slots__ = ()
