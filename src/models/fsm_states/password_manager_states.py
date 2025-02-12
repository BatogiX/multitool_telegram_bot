from aiogram.fsm.state import StatesGroup, State


class PasswordManagerStates(StatesGroup):
    CreatePassword = State()
    CreateService = State()
    EnteringService = State()
    ChangeService = State()
    ConfirmDeletingServices = State()
    ConfirmDeletingService = State()
    ConfirmDeletingPassword = State()
