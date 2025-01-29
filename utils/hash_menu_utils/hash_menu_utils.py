from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import CallbackQuery

from callback_data import HashMenu
from fsm import HashMenuStates
from .calculate_hash import CalculateHash


class HashMenuUtils(CalculateHash):
    _HASH_TO_STATE_MAPPING = {
        HashMenu.hash_types.MD5: HashMenuStates.MD5,
        HashMenu.hash_types.SHA1: HashMenuStates.SHA1,
        HashMenu.hash_types.SHA256: HashMenuStates.SHA256,
    }

    @classmethod
    def _get_hash_type_and_state(cls, data: str) -> tuple[str, State]:
        _, hash_type = data.split(":")
        return hash_type, cls._HASH_TO_STATE_MAPPING.get(hash_type) # noqa

    @classmethod
    async def extract_cb_and_set_state(cls, callback_query: CallbackQuery, state: FSMContext) -> None:
        hash_type, new_state = cls._get_hash_type_and_state(callback_query.data)

        await state.set_state(new_state)
        await state.set_data({"message_to_delete": callback_query.message.message_id})