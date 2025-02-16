from aiogram.filters.callback_data import CallbackData

from config import bot_config as c


class PasswordManagerCallbackData:
    class Enter(CallbackData, prefix="pm_enter", sep=c.sep): ...

    class EnterServices(CallbackData, prefix="pm_services", sep=c.sep):
        services_offset: int

    class EnterService(CallbackData, prefix="pm_service", sep=c.sep):
        service: str
        pwd_offset: int

    class EnterPassword(CallbackData, prefix="pm_pwd", sep=c.sep):
        login: str
        password: str

    class CreateService(CallbackData, prefix="pm_create_service", sep=c.sep):
        services_offset: int

    class CreatePassword(CallbackData, prefix="pm_create_password", sep=c.sep):
        service: str

    class DeleteServices(CallbackData, prefix="pm_delete_services", sep=c.sep):
        services_offset: int

    class DeleteService(CallbackData, prefix="pm_delete_service", sep=c.sep):
        service: str

    class DeletePassword(CallbackData, prefix="pm_delete_password", sep=c.sep):
        service: str

    class ChangeService(CallbackData, prefix="pm_change_service", sep=c.sep):
        service: str

    class ImportFromFile(CallbackData, prefix="pm_import_from_file", sep=c.sep): ...

    class ExportToFile(CallbackData, prefix="pm_export_to_file", sep=c.sep): ...