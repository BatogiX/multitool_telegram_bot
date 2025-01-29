from typing import List

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from callback_data import HashMenu, StartMenu


class InlineHashMenuKeyboard:
    @staticmethod
    def hash_menu_keyboard() -> InlineKeyboardMarkup:
        hash_buttons: List[InlineKeyboardButton] = [
            InlineKeyboardButton(
                text=hash, callback_data=HashMenu(action=hash).pack()
            )
            for hash in HashMenu.hash_types
        ]

        return_to_start_menu_button = InlineKeyboardButton(text="⬅️", callback_data=StartMenu(action=StartMenu.ACTIONS.ENTER).pack())

        return InlineKeyboardMarkup(inline_keyboard=[
            hash_buttons,
            [return_to_start_menu_button]
        ])

    @staticmethod
    def return_to_hash_menu_keyboard() -> InlineKeyboardMarkup:
        return_to_hash_menu_button = InlineKeyboardButton(text="⬅️", callback_data=HashMenu(action=HashMenu.ACTIONS.ENTER).pack())

        return InlineKeyboardMarkup(inline_keyboard=[[return_to_hash_menu_button]])

    @staticmethod
    def return_to_hash_menu_or_retry_keyboard(hash_type: str) -> InlineKeyboardMarkup:
        return_to_hash_menu_button = InlineKeyboardButton(text="⬅️", callback_data=HashMenu(action=HashMenu.ACTIONS.ENTER).pack())
        retry_button = InlineKeyboardButton(text="🔄️", callback_data=HashMenu(action=hash_type).pack())

        return InlineKeyboardMarkup(inline_keyboard=[
            [return_to_hash_menu_button, retry_button]
        ])
