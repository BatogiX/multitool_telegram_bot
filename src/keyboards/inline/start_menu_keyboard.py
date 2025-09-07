from __future__ import annotations

from typing import Final

from aiogram.types import InlineKeyboardMarkup

from keyboards.buttons.start_menu import BTN_GENERATE_RANDOM_PASSWORD, BTN_HASH_MENU, BTN_PASSWORD_MANAGER_MENU


def _start_menu_ikm() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [BTN_HASH_MENU, BTN_PASSWORD_MANAGER_MENU],
            [BTN_GENERATE_RANDOM_PASSWORD],
        ],
    )


START_MENU_IKM: Final[InlineKeyboardMarkup] = _start_menu_ikm()
