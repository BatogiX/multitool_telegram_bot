from aiogram.filters.callback_data import CallbackData

from config import BOT_CFG


class PasswordManagerCallbackData:
    class Enter(CallbackData, prefix="pm_enter", sep=BOT_CFG.sep): ...

    class ImportFromFile(CallbackData, prefix="pm_import_from_file", sep=BOT_CFG.sep): ...

    class ExportToFile(CallbackData, prefix="pm_export_to_file", sep=BOT_CFG.sep): ...

    class ChangeMasterPassword(CallbackData, prefix="pm_change_master_pwd", sep=BOT_CFG.sep): ...

    class EnterServices(CallbackData, prefix="pmesvcs", sep=BOT_CFG.sep):
        services_offset: int

    class DeleteServices(CallbackData, prefix="pmdsvcs", sep=BOT_CFG.sep):
        services_offset: int

    class CreateService(CallbackData, prefix="pmasvc", sep=BOT_CFG.sep):
        services_offset: int

    class EnterService(CallbackData, prefix="pmesvc", sep=BOT_CFG.sep):
        service: str
        services_offset: int
        pwds_offset: int

    class DeleteService(CallbackData, prefix="pmdsvc", sep=BOT_CFG.sep):
        service: str
        services_offset: int
        pwds_offset: int

    class ChangeService(CallbackData, prefix="pmcsvc", sep=BOT_CFG.sep):
        service: str
        services_offset: int
        pwds_offset: int

    class CreatePassword(CallbackData, prefix="pmapwd", sep=BOT_CFG.sep):
        service: str
        services_offset: int
        pwds_offset: int

    class DeletePassword(CallbackData, prefix="pmdpwd", sep=BOT_CFG.sep):
        login: str
        password: str

    class EnterPassword(CallbackData, prefix="pmepwd", sep=BOT_CFG.sep):
        login: str
        password: str

    class UpdateCredentials(CallbackData, prefix="pmucrd", sep=BOT_CFG.sep):
        login: str
        password: str
