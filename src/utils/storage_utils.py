from aiogram.fsm.context import FSMContext

from models.kv import MessageIdToDelete, Service, HashType, PasswordManagerInputFormat
from models.kv.pm_pwd_offset import PasswordManagerPasswordsOffset
from models.kv.pm_services_offset import PasswordManagerServicesOffset


class StorageUtils:
    @staticmethod
    async def _get_data(state: FSMContext, key: str) -> any:
        data = await state.get_data()
        return data.get(key)

    @staticmethod
    async def set_message_id_to_delete(state: FSMContext, message_id: int) -> None:
        await state.update_data(MessageIdToDelete(message_id))

    @classmethod
    async def get_message_id_to_delete(cls, state: FSMContext) -> int:
        return await cls._get_data(state, MessageIdToDelete.key)

    @staticmethod
    async def set_service(state: FSMContext, service_name: str) -> None:
        await state.update_data(Service(service_name))

    @classmethod
    async def get_service(cls, state: FSMContext) -> str:
        return await cls._get_data(state, Service.key)

    @classmethod
    async def set_hash_type(cls, state: FSMContext, hash_type: str) -> None:
        await state.update_data(HashType(hash_type))

    @classmethod
    async def get_hash_type(cls, state: FSMContext) -> str:
        return await cls._get_data(state, HashType.key)

    @classmethod
    async def set_pm_input_format_text(cls, state: FSMContext, text: str) -> None:
        await state.update_data(PasswordManagerInputFormat(text))

    @classmethod
    async def get_pm_input_format_text(cls, state: FSMContext) -> str:
        return await cls._get_data(state, PasswordManagerInputFormat.key)

    @classmethod
    async def set_pm_pwd_offset(cls, state: FSMContext, offset: int) -> None:
        await state.update_data(PasswordManagerPasswordsOffset(offset))

    @classmethod
    async def get_pm_pwd_offset(cls, state: FSMContext) -> int:
        return await cls._get_data(state, PasswordManagerPasswordsOffset.key)

    @classmethod
    async def set_pm_services_offset(cls, state: FSMContext, offset: int) -> None:
        await state.update_data(PasswordManagerServicesOffset(offset))

    @classmethod
    async def get_pm_services_offset(cls, state: FSMContext) -> int:
        return await cls._get_data(state, PasswordManagerServicesOffset.key)