from .inline_hash_menu_keyboard import InlineHashMenuKeyboard
from .inline_start_menu_keyboard import InlineStartMenuKeyboard
from .reply_keyboards_keyboard import PassClass


class InlineKeyboards(InlineHashMenuKeyboard, InlineStartMenuKeyboard):
    __slots__ = ()


class ReplyKeyboards(PassClass):
    __slots__ = ()


__all__ = ['InlineKeyboards', 'ReplyKeyboards']
