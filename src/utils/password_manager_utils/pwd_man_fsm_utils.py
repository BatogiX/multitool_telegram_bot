from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from cryptography.exceptions import InvalidTag

from config import db_manager
from keyboards import InlineKeyboards
from models.passwords_record import WeakPasswordException, EncryptedRecord, DecryptedRecord
from .pwd_man_utils import PasswordManagerUtils as PwManUtils
from .. import BotUtils
from ..fsm_data_utils import FSMDataUtils
from models.callback_data import PasswordManagerCallbackData as PwManCbData
from config import bot_config as c

MAX_CHAR_LIMIT: int = 64


class PasswordManagerFsmHandlerUtils:
    @staticmethod
    async def derive_key_from_master_password(master_password: str, message: Message) -> bytes | str:
        """Validates a master password, derives a key, and verifies correctness."""
        try:
            PwManUtils.validate_master_password(master_password)
        except WeakPasswordException as e:
            return str(e)

        salt: bytes = await db_manager.relational_db.get_salt(message.from_user.id)
        key: bytes = PwManUtils.derive_key(master_password, salt)
        rand_encrypted_record: EncryptedRecord = await db_manager.relational_db.get_rand_passwords_record(message.from_user.id)

        if rand_encrypted_record:
            try:
                PwManUtils.decrypt_record(encrypted_record=rand_encrypted_record, key=key)
            except InvalidTag:
                return ""
        return key

    @staticmethod
    async def show_service_logins(message: Message, state: FSMContext, key: bytes, service: str) -> None:
        pwd_offset: int = await FSMDataUtils.get_pm_pwd_offset(state)
        services_offset: int = await FSMDataUtils.get_pm_services_offset(state)
        encrypted_records: list[EncryptedRecord] = await db_manager.relational_db.get_passwords_records(
            user_id=message.from_user.id,
            service=service,
            offset=pwd_offset
        )
        decrypted_records: list[DecryptedRecord] = []
        for encrypted_record in encrypted_records:
            decrypted_record: DecryptedRecord = PwManUtils.decrypt_record(encrypted_record=encrypted_record, key=key)
            decrypted_records.append(decrypted_record)
        text: str = (
            f"*Service:* {service}\n"
            "Choose your login to see password"
        )
        await message.answer(
            text=text,
            reply_markup=InlineKeyboards.passwd_man_passwords(decrypted_records, service, pwd_offset, services_offset),
            parse_mode="Markdown"
        )

    @staticmethod
    def has_valid_input_length(login: str, password: str) -> bool:
        """Checks if the combined input length exceeds the max character limit."""
        return len(f"{PwManCbData.EnterPassword.__prefix__}{c.sep}{login}{c.sep}{password}") <= MAX_CHAR_LIMIT

    @staticmethod
    async def create_password_record(login: str, password: str, service: str, message: Message, key: bytes) -> None:
        record: str = f"{login}{c.sep}{password}"
        encrypted_record: EncryptedRecord = PwManUtils.encrypt_record(record=record, key=key)
        await db_manager.relational_db.create_password_record(
            user_id=message.from_user.id,
            service=service,
            iv=encrypted_record.iv,
            tag=encrypted_record.tag,
            ciphertext=encrypted_record.ciphertext
        )

    @staticmethod
    async def split_user_input(message: Message, maxsplit: int, sep: str = c.sep) -> tuple:
        parts = tuple(message.text.split(sep=sep))
        return parts if len(parts) == maxsplit else tuple()

    @staticmethod
    async def resend_user_input_request(
            state: FSMContext,
            message: Message,
            error_message: str,
            current_state: str,
    ) -> None:
        await state.set_state(current_state)
        input_format: str = await FSMDataUtils.get_pm_input_format_text(state)
        message_to_delete: Message = await message.answer(
            text=f"{error_message}\n\n{input_format}",
            reply_markup=InlineKeyboards.return_to_passwd_man(offset=0)
        )
        await FSMDataUtils.set_message_to_delete(state, message_to_delete.message_id)

    @staticmethod
    async def handle_message_deletion(state: FSMContext, message: Message) -> str:
        current_state: str = await state.get_state()
        await state.set_state(None)
        await BotUtils.delete_fsm_message(state, message)
        await message.delete()
        return current_state