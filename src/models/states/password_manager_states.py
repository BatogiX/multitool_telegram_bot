from aiogram.fsm.state import State, StatesGroup


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
    ChangeMasterPassword = State()
    UpdateCredentials = State()
