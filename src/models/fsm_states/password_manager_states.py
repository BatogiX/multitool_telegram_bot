from aiogram.fsm.state import StatesGroup, State


class PasswordManagerStates(StatesGroup):
    CreatePassword = State()
    CreateService = State()
    EnterService = State()
    ChangeService = State()
    DeleteServices = State()
    DeleteService = State()
    DeletePassword = State()
    ImportFromFile = State()
    ExportToFile = State()
