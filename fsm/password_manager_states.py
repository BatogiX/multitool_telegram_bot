from aiogram.fsm.state import StatesGroup, State


class PasswordManagerStates(StatesGroup):
    ReadMasterPassword = State()
