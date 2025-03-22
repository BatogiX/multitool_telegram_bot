from aiogram.filters.callback_data import CallbackData

from config import bot_cfg


class PasswordManagerCallbackData:
    class Enter(CallbackData, prefix="pm_enter", sep=bot_cfg.sep): ...

    class EnterServices(CallbackData, prefix="pm_services", sep=bot_cfg.sep):
        services_offset: int

    class EnterService(CallbackData, prefix="pm_service", sep=bot_cfg.sep):
        service: str
        services_offset: int
        pwds_offset: int

    class EnterPassword(CallbackData, prefix="pm_pwd", sep=bot_cfg.sep):
        #   Sensitive data stores in Callback but not in database
        login: str
        password: str

    class CreateService(CallbackData, prefix="pm_create_service", sep=bot_cfg.sep):
        services_offset: int

    class CreatePassword(CallbackData, prefix="pm_create_password", sep=bot_cfg.sep):
        service: str

    class DeleteServices(CallbackData, prefix="pm_delete_services", sep=bot_cfg.sep):
        services_offset: int

    class DeleteService(CallbackData, prefix="pm_delete_service", sep=bot_cfg.sep):
        service: str

    class DeletePassword(CallbackData, prefix="pm_delete_password", sep=bot_cfg.sep):
        service: str

    class ChangeService(CallbackData, prefix="pm_change_service", sep=bot_cfg.sep):
        service: str

    class ImportFromFile(CallbackData, prefix="pm_import_from_file", sep=bot_cfg.sep): ...

    class ExportToFile(CallbackData, prefix="pm_export_to_file", sep=bot_cfg.sep): ...
