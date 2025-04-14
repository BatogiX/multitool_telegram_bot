from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.buttons import (
    gen_hash_buttons,
    gen_return_to_start_menu_button,
    gen_return_to_hash_menu_button,
    gen_retry_same_hash_button
)


def hash_menu() -> InlineKeyboardMarkup:
    hash_buttons: list[InlineKeyboardButton] = gen_hash_buttons()
    return_to_start_menu_button: InlineKeyboardButton = gen_return_to_start_menu_button()

    return InlineKeyboardMarkup(inline_keyboard=[
        hash_buttons,
        [return_to_start_menu_button]
    ])


def return_to_hash_menu() -> InlineKeyboardMarkup:
    return_to_hash_menu_button: InlineKeyboardButton = gen_return_to_hash_menu_button()

    return InlineKeyboardMarkup(inline_keyboard=[[return_to_hash_menu_button]])


def return_to_hash_menu_or_retry(hash_type: str) -> InlineKeyboardMarkup:
    return_to_hash_menu_button: InlineKeyboardButton = gen_return_to_hash_menu_button()
    retry_button: InlineKeyboardButton = gen_retry_same_hash_button(hash_type)

    return InlineKeyboardMarkup(inline_keyboard=[
        [return_to_hash_menu_button, retry_button]
    ])
