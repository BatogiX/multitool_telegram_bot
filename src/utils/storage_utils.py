from aiogram.fsm.context import FSMContext

from models.kv import (
    MessageIdToDelete,
    Service,
    HashType,
    PasswordManagerInputFormat,
    PasswordManagerPasswordsOffset,
    PasswordManagerServicesOffset,
)


class StorageUtils:
    @staticmethod
    async def set_message_id_to_delete(state: FSMContext, message_id: int) -> None:
        await state.update_data(MessageIdToDelete(message_id))

    @staticmethod
    async def set_service(state: FSMContext, service_name: str) -> None:
        await state.update_data(Service(service_name))

    @staticmethod
    async def set_hash_type(state: FSMContext, hash_type: str) -> None:
        await state.update_data(HashType(hash_type))

    @staticmethod
    async def set_pm_input_format_text(state: FSMContext, text: str) -> None:
        await state.update_data(PasswordManagerInputFormat(text))

    @staticmethod
    async def set_pm_pwd_offset(state: FSMContext, offset: int) -> None:
        await state.update_data(PasswordManagerPasswordsOffset(offset))

    @staticmethod
    async def set_pm_services_offset(state: FSMContext, offset: int) -> None:
        await state.update_data(PasswordManagerServicesOffset(offset))

    @staticmethod
    async def get_message_id_to_delete(state: FSMContext) -> int:
        return await state.get_value(MessageIdToDelete.key)

    @staticmethod
    async def get_service(state: FSMContext) -> str:
        return await state.get_value(Service.key)

    @staticmethod
    async def get_hash_type(state: FSMContext) -> str:
        return await state.get_value(HashType.key)

    @staticmethod
    async def get_pm_input_format_text(state: FSMContext) -> str:
        return await state.get_value(PasswordManagerInputFormat.key)

    @staticmethod
    async def get_pm_pwd_offset(state: FSMContext) -> int:
        return await state.get_value(PasswordManagerPasswordsOffset.key)

    @staticmethod
    async def get_pm_services_offset(state: FSMContext) -> int:
        return await state.get_value(PasswordManagerServicesOffset.key)
