from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup

from keyboards.buttons import gen_rand_pwd, start_menu


def _rand_pwd_ikm() -> InlineKeyboardMarkup:
    btn_return_to_start_menu = start_menu.BTN_RETURN_TO_START_MENU
    btn_regenerate_rand_pwd = gen_rand_pwd.BTN_REGENERATE_RAND_PWD

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [btn_return_to_start_menu, btn_regenerate_rand_pwd],
        ],
    )


RAND_PWD_IKM = _rand_pwd_ikm()
