from typing import Callable

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton

from config import bot_cfg

RETURN_CHAR = "⬅️"
PREVIOUS_PAGE_CHAR = "◀️"
NEXT_PAGE_CHAR = "▶️"


def create_button(text: str, callback_data: CallbackData) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=text,
        callback_data=callback_data.pack()
    )


def gen_dynamic_buttons(items: list, create_button_fn: Callable) -> list[list[InlineKeyboardButton]]:
    return [
        [
            create_button_fn(items[i + j])
            for j in range(min(bot_cfg.dynamical_buttons_per_row, len(items) - i))
        ] for i in range(0, len(items), bot_cfg.dynamical_buttons_per_row)
    ]
