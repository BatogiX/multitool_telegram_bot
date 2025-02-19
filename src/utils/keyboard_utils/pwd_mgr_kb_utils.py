from aiogram.types import InlineKeyboardButton

from models.db_record.password_record import DecryptedRecord
from .kb_utils import KeyboardsUtils
from models.callback_data import PasswordManagerCallbackData as PwdMgrCb
from config import bot_cfg


class PasswordManagerKeyboardsUtils(KeyboardsUtils):
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
    def gen_return_to_services_button(cls, offset: int) -> InlineKeyboardButton:
        return cls._create_button(
            text=f"{cls.return_char} {cls.return_to_services_text}",
            callback_data=PwdMgrCb.EnterServices(services_offset=offset)
        )

    @classmethod
    def gen_create_service_button(cls, offset: int) -> InlineKeyboardButton:
        create_new_service_button = cls._create_button(
            text=cls.create_service_text,
            callback_data=PwdMgrCb.CreateService(services_offset=offset)
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
    def gen_delete_services_button(cls, offset: int) -> InlineKeyboardButton | None:
        return cls._create_button(
            text=cls.delete_services_text,
            callback_data=PwdMgrCb.DeleteServices(services_offset=offset)
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
    def gen_service_buttons(cls, services: list[str]) -> list[list[InlineKeyboardButton]]:
        def create_button(service: str) -> InlineKeyboardButton:
            return cls._create_button(
                text=service,
                callback_data=PwdMgrCb.EnterService(service=service, pwd_offset=0)
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
    def gen_previous_page_services_button(cls, offset: int) -> InlineKeyboardButton | None:
        return cls._create_button(
            text=cls.previous_page_char,
            callback_data=PwdMgrCb.EnterServices(services_offset=offset - bot_cfg.dynamic_buttons_limit)
        ) if offset > 0 else None

    @classmethod
    def gen_next_page_services_button(cls, services: list[str], offset: int) -> InlineKeyboardButton | None:
        if len(services) > bot_cfg.dynamic_buttons_limit:
            services.pop()
            return cls._create_button(
                text=cls.next_page_char,
                callback_data=PwdMgrCb.EnterServices(services_offset=offset + bot_cfg.dynamic_buttons_limit)
            )
        return None

    @classmethod
    def gen_previous_page_pwds_button(cls, offset: int, service: str) -> InlineKeyboardButton | None:
        return cls._create_button(
            text=cls.previous_page_char,
            callback_data=PwdMgrCb.EnterService(service=service, pwd_offset=offset - bot_cfg.dynamic_buttons_limit)
        ) if offset > 0 else None

    @classmethod
    def gen_next_page_pwds_button(cls, decrypted_records: list[DecryptedRecord], offset: int, service: str) -> InlineKeyboardButton | None:
        if len(decrypted_records) > bot_cfg.dynamic_buttons_limit:
            decrypted_records.pop()
            return cls._create_button(
                text=cls.next_page_char,
                callback_data=PwdMgrCb.EnterService(service=service, pwd_offset=offset + bot_cfg.dynamic_buttons_limit)
            )
        return None

    @classmethod
    def gen_enter_services_button(cls):
        return cls._create_button(
            text=cls.enter_services_text,
            callback_data=PwdMgrCb.EnterServices(services_offset=0)
        )

    @classmethod
    def gen_import_from_file_button(cls):
        return cls._create_button(
            text=cls.import_from_file_text,
            callback_data=PwdMgrCb.ImportFromFile()
        )

    @classmethod
    def gen_export_to_file_button(cls):
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
            callback_data=PwdMgrCb.EnterService(service=service, pwd_offset=0)
        )