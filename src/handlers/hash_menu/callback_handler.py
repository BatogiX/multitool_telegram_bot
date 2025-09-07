from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import keyboards.inline
from database import db
from helpers.hash_menu import get_state_by_hash_type
from models.callback_data import HashMenuCallbackData as HashMenuCb
from models.states import HashMenuStates

callback_router = Router(name=__name__)

HASH_MENU_ENTER_TEXT = "Choose hash option"
HASH_SELECTION_TEXT = "Upload file and enter expected output in caption"


@callback_router.callback_query(HashMenuCb.Enter.filter())
async def enter_hash_menu(callback_query: CallbackQuery, state: FSMContext) -> None:
    if isinstance(callback_query.message, Message):
        if await db.nosql.get_state() in HashMenuStates:
            await db.nosql.clear_state(state)

        await callback_query.message.edit_text(
            text=HASH_MENU_ENTER_TEXT,
            reply_markup=keyboards.inline.HASH_MENU_IKM,
        )


@callback_router.callback_query(HashMenuCb.Hashes.filter())
async def handle_hash_selection(
    callback_query: CallbackQuery,
    state: FSMContext,
    callback_data: HashMenuCb.Hashes,
) -> Message:
    hash_type = callback_data.hash_type
    new_state = get_state_by_hash_type(hash_type)

    coroutines = [
        db.nosql.set_hash_type(hash_type, state),
        db.nosql.set_state(new_state.state, state),
        db.nosql.set_message_id_to_delete(callback_query.message.message_id, state),
    ]
    await db.nosql.execute(*coroutines)

    return await callback_query.message.edit_text(
        text=HASH_SELECTION_TEXT,
        reply_markup=keyboards.inline.RETURN_TO_HASH_MENU_IKM,
    )
