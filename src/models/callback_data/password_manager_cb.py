from enum import Enum

from aiogram.filters.callback_data import CallbackData

from config import sep as sep


class PasswordManagerCallbackData:


    class PasswordManager(CallbackData, prefix="pm", sep=sep):
        action: str

        class ACTIONS(str, Enum):
            ENTER = "enter"
            CREATE_SERVICE = "new_service"
            DELETE_SERVICES = "del_services"
            DELETE_PASSWORD = "del_pw"


    class EnteringService(CallbackData, prefix="pm_services", sep=sep):
        service: str


    class EnteringPassword(CallbackData, prefix="pm_pw", sep=sep):
        login: str
        password: str


    class ChangeService(CallbackData, prefix="pm_change_service", sep=sep):
        service: str


    class CreatePassword(CallbackData, prefix="pm_create_password", sep=sep):
        service: str


    class DeleteService(CallbackData, prefix="pm_delete_service", sep=sep):
        service: str
