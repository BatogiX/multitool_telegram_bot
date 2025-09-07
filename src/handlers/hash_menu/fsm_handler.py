from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.markdown import text

import keyboards.inline
from database import db
from helpers.hash_menu import check_hash
from models.states import HashMenuStates
from utils import delete_fsm_message

from .callback_handler import HASH_MENU_ENTER_TEXT

fsm_router = Router(name=__name__)


@fsm_router.message(StateFilter(HashMenuStates), F.document)
async def process_check_hash(message: Message, state: FSMContext) -> Message:
    coroutines = [
        db.nosql.get_message_id_to_delete(state),
        db.nosql.clear_state(state),
    ]
    message_id, _ = db.nosql.execute(*coroutines)

    await delete_fsm_message(message_id, message)

    try:
        is_match, expected_hash, hash_type, computed_hash = await check_hash(state, message)
    except Exception as e:
        return await message.answer(
            text=f"{e!s}\n\n{HASH_MENU_ENTER_TEXT}",
            reply_markup=keyboards.inline.HASH_MENU_IKM,
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
        reply_markup=keyboards.inline.return_to_hash_menu_or_retry_ikm(hash_type),
    )
