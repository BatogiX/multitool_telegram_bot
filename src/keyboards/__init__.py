from .inline_keyboards import InlineHashMenuKeyboard
from .inline_keyboards import InlinePasswordManagerKeyboard
from .inline_keyboards import InlineStartMenuKeyboard
from .reply_keyboards import PassClass

__all__ = (
    'InlineKeyboards',
    'ReplyKeyboards'
)


class InlineKeyboards(InlineHashMenuKeyboard, InlineStartMenuKeyboard, InlinePasswordManagerKeyboard):
    __slots__ = ()


class ReplyKeyboards(PassClass):
    __slots__ = ()
