from aiogram.fsm.state import State

from .calculate_hash import CalculateHash


class HashMenuUtils(CalculateHash):

    @classmethod
    async def get_state_by_hash_type(cls, hash_type: str) -> State:
        return cls._HASH_TO_STATE_MAPPING.get(hash_type)
