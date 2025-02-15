from aiogram.types import InlineKeyboardButton

from models.passwords_record import DecryptedRecord
from .keyboards_utils import KeyboardsUtils
from models.callback_data import PasswordManagerCallbackData as PwManCb
from config import bot_config as c


class PasswordManagerKeyboardsUtils(KeyboardsUtils):
    return_to_passwd_man_text = "Back to Password Manager"
    create_service_text = "➕ New service"
    create_password_text = "➕ New password"
    delete_services_text = "❌ Delete services"
    change_service_text = "🔄 Change service's name"
    delete_service_text = "❌ Delete this service"
    delete_password_text = "❌ Delete this password"

    @classmethod
    def gen_return_to_passwd_man_button(cls, offset: int) -> InlineKeyboardButton:
        return cls._create_button(
            text=f"{cls.return_char} {cls.return_to_passwd_man_text}",
            callback_data=PwManCb.Enter(services_offset=offset)
        )

    @classmethod
    def gen_create_service_button(cls, offset: int) -> InlineKeyboardButton:
        create_new_service_button = cls._create_button(
            text=cls.create_service_text,
            callback_data=PwManCb.CreateService(services_offset=offset)
        )
        return create_new_service_button

    @classmethod
    def gen_create_password_button(cls, service: str) -> InlineKeyboardButton:
        create_new_service_button = cls._create_button(
            text=cls.create_password_text,
            callback_data=PwManCb.CreatePassword(service=service)
        )
        return create_new_service_button

    @classmethod
    def gen_delete_services_button(cls, services: list[str], offset: int) -> InlineKeyboardButton | None:
        return cls._create_button(
            text=cls.delete_services_text,
            callback_data=PwManCb.DeleteServices(services_offset=offset)
        ) if services else None

    @classmethod
    def gen_change_service_button(cls, service: str) -> InlineKeyboardButton:
        return cls._create_button(
            text=cls.change_service_text,
            callback_data=PwManCb.ChangeService(service=service)
        )

    @classmethod
    def gen_delete_service_button(cls, service: str) -> InlineKeyboardButton:
        return cls._create_button(
            text=cls.delete_service_text,
            callback_data=PwManCb.DeleteService(service=service)
        )

    @classmethod
    def gen_delete_password_button(cls, service: str) -> InlineKeyboardButton:
        return cls._create_button(
            text=cls.delete_password_text,
            callback_data=PwManCb.DeletePassword(service=service)
        )

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
    def gen_previous_page_services_button(cls, offset: int) -> InlineKeyboardButton | None:
        return cls._create_button(
            text=cls.previous_page_char,
            callback_data=PwManCb.Enter(services_offset=offset - c.dynamic_buttons_limit)
        ) if offset > 0 else None

    @classmethod
    def gen_next_page_services_button(cls, services: list[str], offset: int) -> InlineKeyboardButton | None:
        if len(services) > c.dynamic_buttons_limit:
            services.pop()
            return cls._create_button(
                text=cls.next_page_char,
                callback_data=PwManCb.Enter(services_offset=offset + c.dynamic_buttons_limit)
            )
        return None

    @classmethod
    def gen_previous_page_passwords_button(cls, offset: int, service: str) -> InlineKeyboardButton | None:
        return cls._create_button(
            text=cls.previous_page_char,
            callback_data=PwManCb.EnterService(service=service, pwd_offset=offset - c.dynamic_buttons_limit)
        ) if offset > 0 else None

    @classmethod
    def gen_next_page_passwords_button(cls, decrypted_records: list[DecryptedRecord], offset: int, service: str) -> InlineKeyboardButton | None:
        if len(decrypted_records) > c.dynamic_buttons_limit:
            decrypted_records.pop()
            return cls._create_button(
                text=cls.next_page_char,
                callback_data=PwManCb.EnterService(service=service, pwd_offset=offset + c.dynamic_buttons_limit)
            )
        return None