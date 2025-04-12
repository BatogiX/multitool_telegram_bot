from __future__ import annotations
from typing import Optional

from aiogram.types import InlineKeyboardButton

from utils.kb_utils import create_button, gen_dynamic_buttons
from models.callback_data import PasswordManagerCallbackData as PwdMgrCb
from config import bot_cfg

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
return_to_passwords_text = "Back to Passwords"
return_to_password_text = "Back to Password"
search_text = "🔎 Search"
inline_query_search_service = "service="


def gen_return_to_pwd_mgr_button() -> InlineKeyboardButton:
    return create_button(
        text=f"{return_char} {return_to_pwd_mgr_text}",
        callback_data=PwdMgrCb.Enter()
    )


def gen_return_to_services_button( services_offset: int) -> InlineKeyboardButton:
    return create_button(
        text=f"{return_char} {return_to_services_text}",
        callback_data=PwdMgrCb.EnterServices(services_offset=services_offset)
    )


def gen_create_service_button( services_offset: int) -> InlineKeyboardButton:
    create_new_service_button = create_button(
        text=create_service_text,
        callback_data=PwdMgrCb.CreateService(services_offset=services_offset)
    )
    return create_new_service_button


def gen_create_pwd_button( service: str, services_offset: int, pwds_offset: int) -> InlineKeyboardButton:
    create_new_service_button = create_button(
        text=create_password_text,
        callback_data=PwdMgrCb.CreatePassword(service=service, services_offset=services_offset, pwds_offset=pwds_offset)
    )
    return create_new_service_button


def gen_delete_services_button( services_offset: int) -> Optional[InlineKeyboardButton]:
    return create_button(
        text=delete_services_text,
        callback_data=PwdMgrCb.DeleteServices(services_offset=services_offset)
    )


def gen_change_service_button( service: str, services_offset: int, pwds_offset: int) -> InlineKeyboardButton:
    return create_button(
        text=change_service_text,
        callback_data=PwdMgrCb.ChangeService(service=service, services_offset=services_offset, pwds_offset=pwds_offset)
    )


def gen_delete_service_button( service: str, services_offset: int, pwds_offset: int) -> InlineKeyboardButton:
    return create_button(
        text=delete_service_text,
        callback_data=PwdMgrCb.DeleteService(service=service, services_offset=services_offset, pwds_offset=pwds_offset)
    )


def gen_delete_pwd_button( login: str, password: str) -> InlineKeyboardButton:
    return create_button(
        text=delete_password_text,
        callback_data=PwdMgrCb.DeletePassword(login=login, password=password)
    )


def gen_service_buttons( services: list[str], services_offset: int) -> list[list[InlineKeyboardButton]]:
    def create_button(service: str) -> InlineKeyboardButton:
        return create_button(
            text=service,
            callback_data=PwdMgrCb.EnterService(service=service, services_offset=services_offset, pwds_offset=0)
        )

    return gen_dynamic_buttons(services, create_button)


def gen_pwd_buttons(decrypted_records: list[DecryptedRecord]) -> list[list[InlineKeyboardButton]]:
    def create_button(record: DecryptedRecord) -> InlineKeyboardButton:
        return create_button(
            text=record.login,
            callback_data=PwdMgrCb.EnterPassword(login=record.login, password=record.password)
        )

    return gen_dynamic_buttons(decrypted_records, create_button)


def gen_previous_page_services_button(offset: int) -> Optional[InlineKeyboardButton]:
    if offset <= 0:
        return None

    return create_button(
        text=previous_page_char,
        callback_data=PwdMgrCb.EnterServices(services_offset=offset - 1)
    )


def gen_next_page_services_button(services: list[str], offset: int) -> Optional[InlineKeyboardButton]:
    if len(services) <= bot_cfg.dynamic_buttons_limit:
        return None

    services.pop()
    return create_button(
        text=next_page_char,
        callback_data=PwdMgrCb.EnterServices(services_offset=offset + 1)
    )


def gen_previous_page_pwds_button(services_offset: int, pwd_offset: int, service: str) -> Optional[InlineKeyboardButton]:
    if pwd_offset <= 0:
        return None

    return create_button(
        text=previous_page_char,
        callback_data=PwdMgrCb.EnterService(service=service, services_offset=services_offset, pwds_offset=pwd_offset - 1)
    )


def gen_next_page_pwds_button(decrypted_records: list[DecryptedRecord], service: str, services_offset: int, pwds_offset: int) -> Optional[InlineKeyboardButton]:
    if len(decrypted_records) <= bot_cfg.dynamic_buttons_limit:
        return None

    decrypted_records.pop()
    return create_button(
        text=next_page_char,
        callback_data=PwdMgrCb.EnterService(service=service, services_offset=services_offset, pwds_offset=pwds_offset + 1)
    )


def gen_enter_services_button() -> InlineKeyboardButton:
    return create_button(
        text=enter_services_text,
        callback_data=PwdMgrCb.EnterServices(services_offset=0)
    )


def gen_import_from_file_button() -> InlineKeyboardButton:
    return create_button(
        text=import_from_file_text,
        callback_data=PwdMgrCb.ImportFromFile()
    )


def gen_export_to_file_button() -> InlineKeyboardButton:
    return create_button(
        text=export_to_file_text,
        callback_data=PwdMgrCb.ExportToFile()
    )


def gen_search_button() -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=search_text,
        switch_inline_query_current_chat=inline_query_search_service
    )


def gen_inline_query_service_button(service: str) -> InlineKeyboardButton:
    return create_button(
        text=service,
        callback_data=PwdMgrCb.EnterService(service=service, services_offset=0, pwds_offset=0)
    )


def gen_return_to_passwords_button(service: str, services_offset: int, pwds_offset: int) -> InlineKeyboardButton:
    return create_button(
        text=f"{return_char} {return_to_passwords_text}",
        callback_data=PwdMgrCb.EnterService(service=service, services_offset=services_offset, pwds_offset=pwds_offset)
    )


def gen_return_to_password_button(login: str, password: str) -> InlineKeyboardButton:
    return create_button(
        text=f"{return_char} {return_to_password_text}",
        callback_data=PwdMgrCb.EnterPassword(login=login, password=password)
    )
