from __future__ import annotations

from typing import TYPE_CHECKING, Final

from aiogram.types import InlineKeyboardButton

from config import BOT_CFG
from models.callback_data import PasswordManagerCallbackData as PwdMgrCb

from .util import (
    NEXT_PAGE_CHAR,
    PREVIOUS_PAGE_CHAR,
    RETURN_CHAR,
    create_button,
    gen_dynamic_buttons,
)

if TYPE_CHECKING:
    from helpers.pwd_mgr import DecryptedPassword

ENTER_SERVICES_TEXT = "🌐 Services"
IMPORT_FROM_FILE_TEXT = "⬆️📂 Import from file"
EXPORT_TO_FILE_TEXT = "⬇️📁 Export to file"
CHANGE_MASTER_PASSW_TEXT = "🔑 Change Master Password"
CREATE_SERVICE_TEXT = "➕ New service"  # noqa: RUF001
CREATE_PASSW_TEXT = "➕ New password"  # noqa: RUF001
DELETE_SERVICES_TEXT = "❌ Delete services"
CHANGE_SERVICE_TEXT = "🔄 Change service title"
DELETE_SERVICE_TEXT = "❌ Delete this service"
DELETE_PASSW_TEXT = "❌ Delete this password"
UPDATE_CREDENTIALS_TEXT = "🔄 Update Credentials"
RETURN_TO_PASSW_MGR_TEXT = "Back to Password Manager"
RETURN_TO_SERVICES_TEXT = "Back to Services"
RETURN_TO_PASSWORDS_TEXT = "Back to Passwords"
RETURN_TO_PASSW_TEXT = "Back to Password"
SEARCH_TEXT = "🔎 Search"
INLINE_QUERY_SEARCH_SERVICE = "service="


def _btn_return_to_pwd_mgr() -> InlineKeyboardButton:
    return create_button(
        text=f"{RETURN_CHAR} {RETURN_TO_PASSW_MGR_TEXT}",
        callback_data=PwdMgrCb.Enter(),
    )


def btn_return_to_services(services_offset: int) -> InlineKeyboardButton:
    return create_button(
        text=f"{RETURN_CHAR} {RETURN_TO_SERVICES_TEXT}",
        callback_data=PwdMgrCb.EnterServices(services_offset=services_offset),
    )


def btn_create_service(services_offset: int) -> InlineKeyboardButton:
    return create_button(
        text=CREATE_SERVICE_TEXT,
        callback_data=PwdMgrCb.CreateService(services_offset=services_offset),
    )


def btn_create_pwd(
    service: str,
    services_offset: int,
    pwds_offset: int,
) -> InlineKeyboardButton:
    return create_button(
        text=CREATE_PASSW_TEXT,
        callback_data=PwdMgrCb.CreatePassword(
            service=service,
            services_offset=services_offset,
            pwds_offset=pwds_offset,
        ),
    )


def btn_delete_services(services_offset: int) -> InlineKeyboardButton | None:
    return create_button(
        text=DELETE_SERVICES_TEXT,
        callback_data=PwdMgrCb.DeleteServices(services_offset=services_offset),
    )


def btn_change_service(
    service: str,
    services_offset: int,
    pwds_offset: int,
) -> InlineKeyboardButton:
    return create_button(
        text=CHANGE_SERVICE_TEXT,
        callback_data=PwdMgrCb.ChangeService(
            service=service,
            services_offset=services_offset,
            pwds_offset=pwds_offset,
        ),
    )


def btn_delete_service(
    service: str,
    services_offset: int,
    pwds_offset: int,
) -> InlineKeyboardButton:
    return create_button(
        text=DELETE_SERVICE_TEXT,
        callback_data=PwdMgrCb.DeleteService(
            service=service,
            services_offset=services_offset,
            pwds_offset=pwds_offset,
        ),
    )


def btn_delete_pwd(login: str, password: str) -> InlineKeyboardButton:
    return create_button(
        text=DELETE_PASSW_TEXT,
        callback_data=PwdMgrCb.DeletePassword(login=login, password=password),
    )


def btns_service(
    services: list[str],
    services_offset: int,
) -> list[list[InlineKeyboardButton]]:
    def create_button_func(service: str) -> InlineKeyboardButton:
        return create_button(
            text=service,
            callback_data=PwdMgrCb.EnterService(
                service=service,
                services_offset=services_offset,
                pwds_offset=0,
            ),
        )

    return gen_dynamic_buttons(services, create_button_func)


def btns_pwd(decrypted_records: list[DecryptedPassword]) -> list[list[InlineKeyboardButton]]:
    def create_button_func(record: DecryptedPassword) -> InlineKeyboardButton:
        return create_button(
            text=record.login,
            callback_data=PwdMgrCb.EnterPassword(login=record.login, password=record.password),
        )

    return gen_dynamic_buttons(decrypted_records, create_button_func)


def btn_previous_page_services(offset: int) -> InlineKeyboardButton | None:
    if offset == 0:
        return None

    return create_button(
        text=PREVIOUS_PAGE_CHAR,
        callback_data=PwdMgrCb.EnterServices(services_offset=offset - 1),
    )


def btn_next_page_services(
    services: list[str],
    offset: int,
) -> InlineKeyboardButton | None:
    if len(services) <= BOT_CFG.dynamic_buttons_limit:
        return None

    services.pop()
    return create_button(
        text=NEXT_PAGE_CHAR,
        callback_data=PwdMgrCb.EnterServices(services_offset=offset + 1),
    )


def btn_previous_page_pwds(
    services_offset: int,
    pwd_offset: int,
    service: str,
) -> InlineKeyboardButton | None:
    if pwd_offset == 0:
        return None

    return create_button(
        text=PREVIOUS_PAGE_CHAR,
        callback_data=PwdMgrCb.EnterService(
            service=service,
            services_offset=services_offset,
            pwds_offset=pwd_offset - 1,
        ),
    )


def btn_next_page_pwds(
    decrypted_records: list[DecryptedPassword],
    service: str,
    services_offset: int,
    pwds_offset: int,
) -> InlineKeyboardButton | None:
    if len(decrypted_records) <= BOT_CFG.dynamic_buttons_limit:
        return None

    decrypted_records.pop()
    return create_button(
        text=NEXT_PAGE_CHAR,
        callback_data=PwdMgrCb.EnterService(
            service=service,
            services_offset=services_offset,
            pwds_offset=pwds_offset + 1,
        ),
    )


def _btn_enter_services() -> InlineKeyboardButton:
    return create_button(
        text=ENTER_SERVICES_TEXT,
        callback_data=PwdMgrCb.EnterServices(services_offset=0),
    )


def _btn_import_from_file() -> InlineKeyboardButton:
    return create_button(
        text=IMPORT_FROM_FILE_TEXT,
        callback_data=PwdMgrCb.ImportFromFile(),
    )


def _btn_export_to_file() -> InlineKeyboardButton:
    return create_button(
        text=EXPORT_TO_FILE_TEXT,
        callback_data=PwdMgrCb.ExportToFile(),
    )


def _btn_search_service() -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=SEARCH_TEXT,
        switch_inline_query_current_chat=INLINE_QUERY_SEARCH_SERVICE,
    )


def btn_inline_query_service(service: str) -> InlineKeyboardButton:
    return create_button(
        text=service,
        callback_data=PwdMgrCb.EnterService(service=service, services_offset=0, pwds_offset=0),
    )


def btn_return_to_pwds(
    service: str,
    services_offset: int,
    pwds_offset: int,
) -> InlineKeyboardButton:
    return create_button(
        text=f"{RETURN_CHAR} {RETURN_TO_PASSWORDS_TEXT}",
        callback_data=PwdMgrCb.EnterService(
            service=service,
            services_offset=services_offset,
            pwds_offset=pwds_offset,
        ),
    )


def btn_return_to_password(login: str, password: str) -> InlineKeyboardButton:
    return create_button(
        text=f"{RETURN_CHAR} {RETURN_TO_PASSW_TEXT}",
        callback_data=PwdMgrCb.EnterPassword(login=login, password=password),
    )


def _btn_change_master_password() -> InlineKeyboardButton:
    return create_button(
        text=CHANGE_MASTER_PASSW_TEXT,
        callback_data=PwdMgrCb.ChangeMasterPassword(),
    )


def btn_update_credentials(login: str, password: str) -> InlineKeyboardButton:
    return create_button(
        text=UPDATE_CREDENTIALS_TEXT,
        callback_data=PwdMgrCb.UpdateCredentials(login=login, password=password),
    )


BTN_RETURN_TO_PWD_MGR: Final[InlineKeyboardButton] = _btn_return_to_pwd_mgr()
BTN_ENTER_SERVICES: Final[InlineKeyboardButton] = _btn_enter_services()
BTN_IMPORT_FROM_FILE: Final[InlineKeyboardButton] = _btn_import_from_file()
BTN_EXPORT_TO_FILE: Final[InlineKeyboardButton] = _btn_export_to_file()
BTN_SEARCH_SERVICE: Final[InlineKeyboardButton] = _btn_search_service()
BTN_CHANGE_MASTER_PASSWORD: Final[InlineKeyboardButton] = _btn_change_master_password()
