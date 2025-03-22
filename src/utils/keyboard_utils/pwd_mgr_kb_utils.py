from __future__ import annotations
from typing import TYPE_CHECKING, Optional

from aiogram.types import InlineKeyboardButton

from .kb_utils import BaseKeyboardsUtils
from models.callback_data import PasswordManagerCallbackData as PwdMgrCb
from config import bot_cfg
from utils import BotUtils

if TYPE_CHECKING:
    from helpers import PasswordManagerHelper
    DecryptedRecord = PasswordManagerHelper.DecryptedRecord


class PasswordManagerBaseKeyboardsUtils(BaseKeyboardsUtils):
    enter_services_text = "🌐 Services"
    import_from_file_text = "⬆️📂 Import from file"
    export_to_file_text = "⬇️📁 Export to file"
    create_service_text = "➕ New service"
    create_password_text = "➕ New password"
    delete_services_text = "❌ Delete services"
    change_service_text = "🔄 Change service's name"
    delete_service_text = "❌ Delete this service"
    delete_password_text = "❌ Delete this password"
    return_to_pwd_mgr_text = "Back to Password Manager"
    return_to_services_text = "Back to Services"
    search_text = "🔎 Search"
    inline_query_search_service = "service="

    @classmethod
    def gen_return_to_pwd_mgr_button(cls) -> InlineKeyboardButton:
        return cls._create_button(
            text=f"{cls.return_char} {cls.return_to_pwd_mgr_text}",
            callback_data=PwdMgrCb.Enter()
        )

    @classmethod
    def gen_return_to_services_button(cls, services_offset: int) -> InlineKeyboardButton:
        return cls._create_button(
            text=f"{cls.return_char} {cls.return_to_services_text}",
            callback_data=PwdMgrCb.EnterServices(services_offset=services_offset)
        )

    @classmethod
    def gen_create_service_button(cls, services_offset: int) -> InlineKeyboardButton:
        create_new_service_button = cls._create_button(
            text=cls.create_service_text,
            callback_data=PwdMgrCb.CreateService(services_offset=services_offset)
        )
        return create_new_service_button

    @classmethod
    def gen_create_pwd_button(cls, service: str) -> InlineKeyboardButton:
        create_new_service_button = cls._create_button(
            text=cls.create_password_text,
            callback_data=PwdMgrCb.CreatePassword(service=service)
        )
        return create_new_service_button

    @classmethod
    def gen_delete_services_button(cls, services_offset: int) -> Optional[InlineKeyboardButton]:
        return cls._create_button(
            text=cls.delete_services_text,
            callback_data=PwdMgrCb.DeleteServices(services_offset=services_offset)
        )

    @classmethod
    def gen_change_service_button(cls, service: str) -> InlineKeyboardButton:
        return cls._create_button(
            text=cls.change_service_text,
            callback_data=PwdMgrCb.ChangeService(service=service)
        )

    @classmethod
    def gen_delete_service_button(cls, service: str) -> InlineKeyboardButton:
        return cls._create_button(
            text=cls.delete_service_text,
            callback_data=PwdMgrCb.DeleteService(service=service)
        )

    @classmethod
    def gen_delete_pwd_button(cls, service: str) -> InlineKeyboardButton:
        return cls._create_button(
            text=cls.delete_password_text,
            callback_data=PwdMgrCb.DeletePassword(service=service)
        )

    @classmethod
    def gen_service_buttons(cls, services: list[str], services_offset: int) -> list[list[InlineKeyboardButton]]:
        def create_button(service: str) -> InlineKeyboardButton:
            return cls._create_button(
                text=BotUtils.strip_protocol(service),
                callback_data=PwdMgrCb.EnterService(service=service, services_offset=services_offset, pwds_offset=0)
            )

        return cls._gen_dynamic_buttons(services, create_button)

    @classmethod
    def gen_pwd_buttons(cls, decrypted_records: list[DecryptedRecord]) -> list[list[InlineKeyboardButton]]:
        def create_button(record: DecryptedRecord) -> InlineKeyboardButton:
            return cls._create_button(
                text=record.login,
                callback_data=PwdMgrCb.EnterPassword(login=record.login, password=record.password)
            )

        return cls._gen_dynamic_buttons(decrypted_records, create_button)

    @classmethod
    def gen_previous_page_services_button(cls, offset: int) -> Optional[InlineKeyboardButton]:
        if offset <= 0:
            return None

        return cls._create_button(
            text=cls.previous_page_char,
            callback_data=PwdMgrCb.EnterServices(services_offset=offset - 1)
        )

    @classmethod
    def gen_next_page_services_button(cls, services: list[str], offset: int) -> Optional[InlineKeyboardButton]:
        if len(services) <= bot_cfg.dynamic_buttons_limit:
            return None

        services.pop()
        return cls._create_button(
            text=cls.next_page_char,
            callback_data=PwdMgrCb.EnterServices(services_offset=offset + 1)
        )

    @classmethod
    def gen_previous_page_pwds_button(cls, services_offset: int, pwd_offset: int, service: str) -> Optional[InlineKeyboardButton]:
        if pwd_offset <= 0:
            return None

        return cls._create_button(
            text=cls.previous_page_char,
            callback_data=PwdMgrCb.EnterService(service=service, services_offset=services_offset, pwds_offset=pwd_offset - 1)
        )

    @classmethod
    def gen_next_page_pwds_button(cls, decrypted_records: list[DecryptedRecord], services_offset: int, pwds_offset: int, service: str) -> Optional[InlineKeyboardButton]:
        if len(decrypted_records) <= bot_cfg.dynamic_buttons_limit:
            return None

        decrypted_records.pop()
        return cls._create_button(
            text=cls.next_page_char,
            callback_data=PwdMgrCb.EnterService(service=service, services_offset=services_offset, pwds_offset=pwds_offset + 1)
        )

    @classmethod
    def gen_enter_services_button(cls) -> InlineKeyboardButton:
        return cls._create_button(
            text=cls.enter_services_text,
            callback_data=PwdMgrCb.EnterServices(services_offset=0)
        )

    @classmethod
    def gen_import_from_file_button(cls) -> InlineKeyboardButton:
        return cls._create_button(
            text=cls.import_from_file_text,
            callback_data=PwdMgrCb.ImportFromFile()
        )

    @classmethod
    def gen_export_to_file_button(cls) -> InlineKeyboardButton:
        return cls._create_button(
            text=cls.export_to_file_text,
            callback_data=PwdMgrCb.ExportToFile()
        )

    @classmethod
    def gen_search_button(cls) -> InlineKeyboardButton:
        return InlineKeyboardButton(
            text=cls.search_text,
            switch_inline_query_current_chat=cls.inline_query_search_service
        )

    @classmethod
    def gen_inline_query_service_button(cls, service: str) -> InlineKeyboardButton:
        return cls._create_button(
            text=service,
            callback_data=PwdMgrCb.EnterService(service=service, services_offset=0, pwds_offset=0)
        )
