from aiogram.fsm.state import State, StatesGroup


class HashMenuStates(StatesGroup):
    MD5 = State()
    SHA1 = State()
    SHA256 = State()
