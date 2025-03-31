from aiogram.filters.callback_data import CallbackData

from config import bot_cfg


class PasswordManagerCallbackData:
    class Enter(CallbackData, prefix="pm_enter", sep=bot_cfg.sep): ...
    class ImportFromFile(CallbackData, prefix="pm_import_from_file", sep=bot_cfg.sep): ...
    class ExportToFile(CallbackData, prefix="pm_export_to_file", sep=bot_cfg.sep): ...
    class ChangeMasterPassword(CallbackData, prefix="pm_change_master_password", sep=bot_cfg.sep): ...

    class EnterServices(CallbackData, prefix="pmesvcs", sep=bot_cfg.sep):
        services_offset: int

    class DeleteServices(CallbackData, prefix="pmdsvcs", sep=bot_cfg.sep):
        services_offset: int

    class CreateService(CallbackData, prefix="pmasvc", sep=bot_cfg.sep):
        services_offset: int

    class EnterService(CallbackData, prefix="pmesvc", sep=bot_cfg.sep):
        service: str
        services_offset: int
        pwds_offset: int

    class DeleteService(CallbackData, prefix="pmdsvc", sep=bot_cfg.sep):
        service: str
        services_offset: int
        pwds_offset: int

    class ChangeService(CallbackData, prefix="pmcsvc", sep=bot_cfg.sep):
        service: str
        services_offset: int
        pwds_offset: int

    class CreatePassword(CallbackData, prefix="pmapwd", sep=bot_cfg.sep):
        service: str
        services_offset: int
        pwds_offset: int

    class DeletePassword(CallbackData, prefix="pmdpwd", sep=bot_cfg.sep):
        login: str
        password: str

    class EnterPassword(CallbackData, prefix="pmepwd", sep=bot_cfg.sep):
        login: str
        password: str

    class ChangePassword(CallbackData, prefix="pmcpwd", sep=bot_cfg.sep):
        login: str
        password: str

    class ChangeLogin(CallbackData, prefix="pmclog", sep=bot_cfg.sep):
        login: str
        password: str
