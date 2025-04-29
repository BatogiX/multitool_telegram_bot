from __future__ import annotations

from typing import Optional

from aiogram.types import InlineKeyboardButton

from config import bot_cfg
from helpers.pwd_mgr_helper import DecryptedRecord
from models.callback_data import PasswordManagerCallbackData as PwdMgrCb
from utils.kb_utils import create_button, gen_dynamic_buttons, RETURN_CHAR, PREVIOUS_PAGE_CHAR, \
    NEXT_PAGE_CHAR

enter_services_text = "🌐 Services"
import_from_file_text = "⬆️📂 Import from file"
export_to_file_text = "⬇️📁 Export to file"
change_master_password_text = "🔑 Change Master Password"
create_service_text = "➕ New service"
create_password_text = "➕ New password"
delete_services_text = "❌ Delete services"
change_service_text = "🔄 Change service title"
delete_service_text = "❌ Delete this service"
delete_password_text = "❌ Delete this password"
update_credentials_text = "🔄 Update Credentials"
return_to_pwd_mgr_text = "Back to Password Manager"
return_to_services_text = "Back to Services"
return_to_passwords_text = "Back to Passwords"
return_to_password_text = "Back to Password"
search_text = "🔎 Search"
inline_query_search_service = "service="


def _btn_return_to_pwd_mgr() -> InlineKeyboardButton:
    return create_button(
        text=f"{RETURN_CHAR} {return_to_pwd_mgr_text}",
        callback_data=PwdMgrCb.Enter()
    )


def btn_return_to_services(services_offset: int) -> InlineKeyboardButton:
    return create_button(
        text=f"{RETURN_CHAR} {return_to_services_text}",
        callback_data=PwdMgrCb.EnterServices(services_offset=services_offset)
    )


def btn_create_service(services_offset: int) -> InlineKeyboardButton:
    return create_button(
        text=create_service_text,
        callback_data=PwdMgrCb.CreateService(services_offset=services_offset)
    )


def btn_create_pwd(
    service: str, services_offset: int, pwds_offset: int
) -> InlineKeyboardButton:
    return create_button(
        text=create_password_text,
        callback_data=PwdMgrCb.CreatePassword(
            service=service, services_offset=services_offset, pwds_offset=pwds_offset
        )
    )


def btn_delete_services(services_offset: int) -> Optional[InlineKeyboardButton]:
    return create_button(
        text=delete_services_text,
        callback_data=PwdMgrCb.DeleteServices(services_offset=services_offset)
    )


def btn_change_service(
    service: str, services_offset: int, pwds_offset: int
) -> InlineKeyboardButton:
    return create_button(
        text=change_service_text,
        callback_data=PwdMgrCb.ChangeService(
            service=service, services_offset=services_offset, pwds_offset=pwds_offset
        )
    )


def btn_delete_service(
    service: str, services_offset: int, pwds_offset: int
) -> InlineKeyboardButton:
    return create_button(
        text=delete_service_text,
        callback_data=PwdMgrCb.DeleteService(
            service=service, services_offset=services_offset, pwds_offset=pwds_offset
        )
    )


def btn_delete_pwd(login: str, password: str) -> InlineKeyboardButton:
    return create_button(
        text=delete_password_text,
        callback_data=PwdMgrCb.DeletePassword(login=login, password=password)
    )


def btns_service(
    services: list[str], services_offset: int
) -> list[list[InlineKeyboardButton]]:
    def create_button_func(service: str) -> InlineKeyboardButton:
        return create_button(
            text=service,
            callback_data=PwdMgrCb.EnterService(
                service=service, services_offset=services_offset, pwds_offset=0
            )
        )

    return gen_dynamic_buttons(services, create_button_func)


def btns_pwd(decrypted_records: list[DecryptedRecord]) -> list[list[InlineKeyboardButton]]:
    def create_button_func(record: DecryptedRecord) -> InlineKeyboardButton:
        return create_button(
            text=record.login,
            callback_data=PwdMgrCb.EnterPassword(login=record.login, password=record.password)
        )

    return gen_dynamic_buttons(decrypted_records, create_button_func)


def btn_previous_page_services(offset: int) -> Optional[InlineKeyboardButton]:
    if offset == 0:
        return None

    return create_button(
        text=PREVIOUS_PAGE_CHAR,
        callback_data=PwdMgrCb.EnterServices(services_offset=offset - 1)
    )


def btn_next_page_services(
    services: list[str], offset: int
) -> Optional[InlineKeyboardButton]:
    if len(services) <= bot_cfg.dynamic_buttons_limit:
        return None

    services.pop()
    return create_button(
        text=NEXT_PAGE_CHAR,
        callback_data=PwdMgrCb.EnterServices(services_offset=offset + 1)
    )


def btn_previous_page_pwds(
    services_offset: int, pwd_offset: int, service: str
) -> Optional[InlineKeyboardButton]:
    if pwd_offset == 0:
        return None

    return create_button(
        text=PREVIOUS_PAGE_CHAR,
        callback_data=PwdMgrCb.EnterService(
            service=service, services_offset=services_offset, pwds_offset=pwd_offset - 1
        )
    )


def btn_next_page_pwds(
    decrypted_records: list[DecryptedRecord], service: str, services_offset: int, pwds_offset: int
) -> Optional[InlineKeyboardButton]:
    if len(decrypted_records) <= bot_cfg.dynamic_buttons_limit:
        return None

    decrypted_records.pop()
    return create_button(
        text=NEXT_PAGE_CHAR,
        callback_data=PwdMgrCb.EnterService(
            service=service, services_offset=services_offset, pwds_offset=pwds_offset + 1
        )
    )


def _btn_enter_services() -> InlineKeyboardButton:
    return create_button(
        text=enter_services_text,
        callback_data=PwdMgrCb.EnterServices(services_offset=0)
    )


def _btn_import_from_file() -> InlineKeyboardButton:
    return create_button(
        text=import_from_file_text,
        callback_data=PwdMgrCb.ImportFromFile()
    )


def _btn_export_to_file() -> InlineKeyboardButton:
    return create_button(
        text=export_to_file_text,
        callback_data=PwdMgrCb.ExportToFile()
    )


def _btn_search_service() -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=search_text,
        switch_inline_query_current_chat=inline_query_search_service
    )


def btn_inline_query_service(service: str) -> InlineKeyboardButton:
    return create_button(
        text=service,
        callback_data=PwdMgrCb.EnterService(service=service, services_offset=0, pwds_offset=0)
    )


def btn_return_to_pwds(
    service: str, services_offset: int, pwds_offset: int
) -> InlineKeyboardButton:
    return create_button(
        text=f"{RETURN_CHAR} {return_to_passwords_text}",
        callback_data=PwdMgrCb.EnterService(
            service=service, services_offset=services_offset, pwds_offset=pwds_offset
        )
    )


def btn_return_to_password(login: str, password: str) -> InlineKeyboardButton:
    return create_button(
        text=f"{RETURN_CHAR} {return_to_password_text}",
        callback_data=PwdMgrCb.EnterPassword(login=login, password=password)
    )


def _btn_change_master_password() -> InlineKeyboardButton:
    return create_button(
        text=change_master_password_text,
        callback_data=PwdMgrCb.ChangeMasterPassword()
    )


def btn_update_credentials(login: str, password: str) -> InlineKeyboardButton:
    return create_button(
        text=update_credentials_text,
        callback_data=PwdMgrCb.UpdateCredentials(login=login, password=password)
    )


btn_return_to_pwd_mgr: InlineKeyboardButton = _btn_return_to_pwd_mgr()
btn_enter_services: InlineKeyboardButton = _btn_enter_services()
btn_import_from_file: InlineKeyboardButton = _btn_import_from_file()
btn_export_to_file: InlineKeyboardButton = _btn_export_to_file()
btn_search_service: InlineKeyboardButton = _btn_search_service()
btn_change_master_password: InlineKeyboardButton = _btn_change_master_password()
