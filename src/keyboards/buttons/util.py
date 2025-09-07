from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram.types import InlineKeyboardButton

from config import BOT_CFG

if TYPE_CHECKING:
    from collections.abc import Callable

    from aiogram.filters.callback_data import CallbackData

RETURN_CHAR = "⬅️"
PREVIOUS_PAGE_CHAR = "◀️"
NEXT_PAGE_CHAR = "▶️"


def create_button(text: str, callback_data: CallbackData) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=text,
        callback_data=callback_data.pack(),
    )


def gen_dynamic_buttons(
    items: list,
    create_button_fn: Callable,
) -> list[list[InlineKeyboardButton]]:
    return [
        [create_button_fn(items[i + j]) for j in range(min(BOT_CFG.dynamical_buttons_per_row, len(items) - i))]
        for i in range(0, len(items), BOT_CFG.dynamical_buttons_per_row)
    ]
