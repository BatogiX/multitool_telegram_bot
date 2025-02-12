from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton

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
    def gen_return_to_passwd_man_button(cls, text: str = "Back to Password Manager") -> InlineKeyboardButton:
        return cls._create_button(
            text=f"{cls.return_char} {text}",
            callback_data=PwManCb.PasswordManager(action=PwManCb.PasswordManager.ACTIONS.ENTER)
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
            callback_data=PwManCb.PasswordManager(action=PwManCb.PasswordManager.ACTIONS.ENTER)
        )

    @classmethod
    def gen_create_service_button(cls) -> InlineKeyboardButton:
        create_new_service_button = cls._create_button(
            text="➕ New service",
            callback_data=PwManCb.PasswordManager(action=PwManCb.PasswordManager.ACTIONS.CREATE_SERVICE)
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
    def gen_delete_services_button(cls, services: list[str]) -> list[InlineKeyboardButton] | list[None]:
        return [cls._create_button(
            text="❌ Delete services",
            callback_data=PwManCb.PasswordManager(action=PwManCb.PasswordManager.ACTIONS.DELETE_SERVICES)
        )] if services else []

    @classmethod
    def gen_service_buttons(cls, services: list[str]) -> list[InlineKeyboardButton]:
        return [
            cls._create_button(text=service, callback_data=PwManCb.EnteringService(service=service))
            for service in services
        ]

    @classmethod
    def gen_password_buttons(cls, decrypted_records: list[DecryptedRecord]) -> list[InlineKeyboardButton]:
        return [
            cls._create_button(
                text=data.login,
                callback_data=PwManCb.EnteringPassword(login=data.login, password=data.password)
            )
            for data in decrypted_records
        ]

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
    def gen_delete_password_button(cls) -> InlineKeyboardButton:
        return cls._create_button(
            text="❌ Delete this password",
            callback_data=PwManCb.PasswordManager(action=PwManCb.PasswordManager.ACTIONS.DELETE_PASSWORD)
        )

    @classmethod
    def gen_retry_same_hash_button(cls, hash_type: str) -> InlineKeyboardButton:
        return cls._create_button(
            text="🔄️",
            callback_data=HashMenuCallbackData(action=hash_type)
        )
