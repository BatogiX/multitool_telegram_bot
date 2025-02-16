from typing import Callable

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton

from config import bot_config as c


class KeyboardsUtils:
    return_char: str = "⬅️"
    previous_page_char: str = "◀️"
    next_page_char: str = "▶️"

    @staticmethod
    def _create_button(text: str, callback_data: CallbackData) -> InlineKeyboardButton:
        return InlineKeyboardButton(
            text=text,
            callback_data=callback_data.pack()
        )

    @classmethod
    def _gen_dynamic_buttons(cls, items: list, create_button_fn: Callable) -> list[list[InlineKeyboardButton]]:
        return [
            [
                create_button_fn(items[i + j])
                for j in range(min(c.dynamical_buttons_per_row, len(items) - i))
            ] for i in range(0, len(items), c.dynamical_buttons_per_row)
        ]
