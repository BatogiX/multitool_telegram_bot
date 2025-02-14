from typing import Callable

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton

from config import bot_config as c
from models.callback_data import StartMenuCallbackData, PasswordManagerCallbackData as PwManCb, HashMenuCallbackData
from models.passwords_record import DecryptedRecord


class KeyboardsUtils:
    return_char: str = "⬅️"

    @staticmethod
    def _create_button(text: str, callback_data: CallbackData) -> InlineKeyboardButton:
        return InlineKeyboardButton(text=text, callback_data=callback_data.pack())

    @classmethod
    def gen_return_to_start_menu_button(cls, text: str = "Back to Main Menu") -> InlineKeyboardButton:
        return cls._create_button(
            text=f"{cls.return_char} {text}",
            callback_data=StartMenuCallbackData(action=StartMenuCallbackData.ACTIONS.ENTER)
        )

    @classmethod
    def gen_return_to_passwd_man_button(cls, offset: int,
                                        text: str = "Back to Password Manager") -> InlineKeyboardButton:
        return cls._create_button(
            text=f"{cls.return_char} {text}",
            callback_data=PwManCb.Enter(services_offset=offset)
        )

    @classmethod
    def gen_return_to_hash_menu_button(cls, text: str = "Back to Hash Menu") -> InlineKeyboardButton:
        return cls._create_button(
            text=f"{cls.return_char} {text}",
            callback_data=HashMenuCallbackData(action=HashMenuCallbackData.ACTIONS.ENTER)
        )

    @classmethod
    def gen_hash_buttons(cls) -> list[InlineKeyboardButton]:
        return [
            cls._create_button(
                text=hash, callback_data=HashMenuCallbackData(action=hash)
            )
            for hash in HashMenuCallbackData.hash_types
        ]

    @classmethod
    def gen_hash_menu_button(cls) -> InlineKeyboardButton:
        return cls._create_button(
            text="🔍 Verify file's hash",
            callback_data=HashMenuCallbackData(action=HashMenuCallbackData.ACTIONS.ENTER)
        )

    @classmethod
    def gen_password_manager_button(cls) -> InlineKeyboardButton:
        return cls._create_button(
            text="🔐 Password manager",
            callback_data=PwManCb.Enter(services_offset=0)
        )

    @classmethod
    def gen_create_service_button(cls, offset: int) -> InlineKeyboardButton:
        create_new_service_button = cls._create_button(
            text="➕ New service",
            callback_data=PwManCb.Enter(services_offset=offset)
        )
        return create_new_service_button

    @classmethod
    def gen_create_password_button(cls, service: str) -> InlineKeyboardButton:
        create_new_service_button = cls._create_button(
            text="➕ New password",
            callback_data=PwManCb.CreatePassword(service=service)
        )
        return create_new_service_button

    @classmethod
    def gen_delete_services_button(cls, services: list[str], offset: int) -> InlineKeyboardButton | None:
        return cls._create_button(
            text="❌ Delete services",
            callback_data=PwManCb.Enter(services_offset=offset)
        ) if services else None

    @classmethod
    def _gen_dynamic_buttons(cls, items: list, create_button_fn: Callable) -> list[list[InlineKeyboardButton]]:
        return [
            [
                create_button_fn(items[i + j])
                for j in range(min(c.dynamical_buttons_per_row, len(items) - i))
            ] for i in range(0, len(items), c.dynamical_buttons_per_row)
        ]

    @classmethod
    def gen_service_buttons(cls, services: list[str]) -> list[list[InlineKeyboardButton]]:
        def create_button(service: str) -> InlineKeyboardButton:
            return cls._create_button(
                text=service,
                callback_data=PwManCb.EnterService(service=service, pwd_offset=0)
            )

        return cls._gen_dynamic_buttons(services, create_button)

    @classmethod
    def gen_password_buttons(cls, decrypted_records: list[DecryptedRecord]) -> list[list[InlineKeyboardButton]]:
        def create_button(record: DecryptedRecord) -> InlineKeyboardButton:
            return cls._create_button(
                text=record.login,
                callback_data=PwManCb.EnterPassword(login=record.login, password=record.password)
            )

        return cls._gen_dynamic_buttons(decrypted_records, create_button)

    @classmethod
    def gen_change_service_button(cls, service: str) -> InlineKeyboardButton:
        return cls._create_button(
            text="🔄 Change service's name",
            callback_data=PwManCb.ChangeService(service=service)
        )

    @classmethod
    def gen_delete_service_button(cls, service: str) -> InlineKeyboardButton:
        return cls._create_button(
            text="❌ Delete this service",
            callback_data=PwManCb.DeleteService(service=service)
        )

    @classmethod
    def gen_delete_password_button(cls, offset: int) -> InlineKeyboardButton:
        return cls._create_button(
            text="❌ Delete this password",
            callback_data=PwManCb.Enter(services_offset=offset)
        )

    @classmethod
    def gen_retry_same_hash_button(cls, hash_type: str) -> InlineKeyboardButton:
        return cls._create_button(
            text="🔄️",
            callback_data=HashMenuCallbackData(action=hash_type)
        )

    @classmethod
    def gen_previous_page_services_button(cls, offset: int) -> InlineKeyboardButton | None:
        return cls._create_button(
            text="◀️",
            callback_data=PwManCb.Enter(services_offset=offset - c.dynamic_buttons_limit)
        ) if offset > 0 else None

    @classmethod
    def gen_next_page_services_button(cls, services: list[str], offset: int) -> InlineKeyboardButton | None:
        if len(services) > c.dynamic_buttons_limit:
            services.pop()
            return cls._create_button(
                text="▶️",
                callback_data=PwManCb.Enter(services_offset=offset + c.dynamic_buttons_limit)
            )
        return None

    @classmethod
    def gen_previous_page_passwords_button(cls, offset: int, service: str) -> InlineKeyboardButton | None:
        return cls._create_button(
            text="◀️",
            callback_data=PwManCb.EnterService(service=service, pwd_offset=offset - c.dynamic_buttons_limit)
        ) if offset > 0 else None

    @classmethod
    def gen_next_page_passwords_button(cls, decrypted_records: list[DecryptedRecord], offset: int,
                                       service: str) -> InlineKeyboardButton | None:
        if len(decrypted_records) > c.dynamic_buttons_limit:
            decrypted_records.pop()
            return cls._create_button(
                text="▶️",
                callback_data=PwManCb.EnterService(service=service, pwd_offset=offset + c.dynamic_buttons_limit)
            )
        return None
