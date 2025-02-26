from .hash_menu_keyboard import InlineHashMenuKeyboard
from .pwd_mgr_keyboard import InlinePasswordManagerKeyboard
from .start_menu_keyboard import InlineStartMenuKeyboard
from .gen_rand_pwd_keyboard import InlineGenerateRandomPasswordKeyboard


class InlineKeyboards(
    InlineHashMenuKeyboard,
    InlineStartMenuKeyboard,
    InlinePasswordManagerKeyboard,
    InlineGenerateRandomPasswordKeyboard,
):
    __slots__ = ()


__all__ = "InlineKeyboards"
