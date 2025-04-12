from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.markdown import text

from database import db_manager
from helpers.hash_menu_helper import check_hash
from keyboards.inline import hash_menu, return_to_hash_menu_or_retry
from .callback_handler import HASH_MENU_ENTER_TEXT
from models.states import HashMenuStates
from utils import delete_fsm_message

fsm_router = Router(name=__name__)


@fsm_router.message(StateFilter(HashMenuStates), F.document)
async def process_check_hash(message: Message, state: FSMContext) -> Message:
    coroutines = [
        db_manager.key_value_db.get_message_id_to_delete(state),
        db_manager.key_value_db.clear_state(state)
    ]
    message_id, _ = db_manager.key_value_db.execute_batch(*coroutines)

    await delete_fsm_message(message_id, message)

    try:
        is_match, expected_hash, hash_type, computed_hash = await check_hash(state, message)
    except Exception as e:
        return await message.answer(
            text=f"{str(e)}\n\n{HASH_MENU_ENTER_TEXT}",
            reply_markup=hash_menu()
        )

    status = "✅" if is_match else "❌"
    response_text = text(
        f"{status} Expected hash: {status}",
        f"`{expected_hash}`",
        f"{status} {hash_type} hash: {status}",
        f"`{computed_hash}`",
        sep="\n",
    )

    return await message.answer(
        text=response_text,
        parse_mode="Markdown",
        reply_markup=return_to_hash_menu_or_retry(hash_type)
    )
