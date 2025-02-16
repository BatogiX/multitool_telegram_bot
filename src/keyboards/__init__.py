from .inline_keyboards import InlineHashMenuKeyboard, InlinePasswordManagerKeyboard, InlineStartMenuKeyboard

__all__ = "InlineKeyboards"


class InlineKeyboards(InlineHashMenuKeyboard, InlineStartMenuKeyboard, InlinePasswordManagerKeyboard):
    __slots__ = ()

