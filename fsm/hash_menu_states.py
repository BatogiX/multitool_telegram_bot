from aiogram.fsm.state import StatesGroup, State


class HashMenuStates(StatesGroup):
    MD5 = State()
    SHA1 = State()
    SHA256 = State()
