from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.markdown import text

from database import db
from helpers.hash_menu_helper import check_hash
import keyboards.inline
from models.states import HashMenuStates
from utils import delete_fsm_message
from .callback_handler import HASH_MENU_ENTER_TEXT

fsm_router = Router(name=__name__)


@fsm_router.message(StateFilter(HashMenuStates), F.document)
async def process_check_hash(message: Message, state: FSMContext) -> Message:
    coroutines = [
        db.key_value.get_message_id_to_delete(state),
        db.key_value.clear_state(state)
    ]
    message_id, _ = db.key_value.execute_batch(*coroutines)

    await delete_fsm_message(message_id, message)

    try:
        is_match, expected_hash, hash_type, computed_hash = await check_hash(state, message)
    except Exception as e:
        return await message.answer(
            text=f"{str(e)}\n\n{HASH_MENU_ENTER_TEXT}",
            reply_markup=keyboards.inline.hash_menu_ikm
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
        reply_markup=keyboards.inline.return_to_hash_menu_or_retry_ikm(hash_type)
    )
