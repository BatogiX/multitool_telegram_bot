from mailbox import Message

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from database import db
from helpers.hash_menu_helper import get_state_by_hash_type
import keyboards.inline
from models.callback_data import HashMenuCallbackData as HashMenuCb
from models.states import HashMenuStates

callback_router = Router(name=__name__)

HASH_MENU_ENTER_TEXT = "Choose hash option"
HASH_SELECTION_TEXT = "Upload file and enter expected output in caption"


@callback_router.callback_query(HashMenuCb.Enter.filter())
async def enter_hash_menu(callback_query: CallbackQuery, state: FSMContext) -> Message:
    if await db.key_value.get_state(state) in HashMenuStates:
        await db.key_value.clear_state(state)

    return await callback_query.message.edit_text(
        text=HASH_MENU_ENTER_TEXT,
        reply_markup=keyboards.inline.hash_menu_ikm
    )


@callback_router.callback_query(HashMenuCb.Hashes.filter())
async def handle_hash_selection(
    callback_query: CallbackQuery, state: FSMContext, callback_data: HashMenuCb.Hashes
) -> Message:
    hash_type = callback_data.hash_type
    new_state = get_state_by_hash_type(hash_type)

    coroutines = [
        db.key_value.set_hash_type(hash_type, state),
        db.key_value.set_state(new_state.state, state),
        db.key_value.set_message_id_to_delete(callback_query.message.message_id, state)
    ]
    await db.key_value.execute_batch(*coroutines)

    return await callback_query.message.edit_text(
        text=HASH_SELECTION_TEXT,
        reply_markup=keyboards.inline.return_to_hash_menu_ikm
    )
