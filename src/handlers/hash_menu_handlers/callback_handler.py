from mailbox import Message

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import CallbackQuery

from keyboards import Keyboards
from models.callback_data import HashMenuCallbackData as HashMenuCb
from models.states import HashMenuStates
from utils import StorageUtils
from helpers import HashMenuHelper

callback_router = Router(name=__name__)

HASH_MENU_ENTER_TEXT = "Choose hash option"
HASH_SELECTION_TEXT = "Upload file and enter expected output in caption"


@callback_router.callback_query(HashMenuCb.Enter.filter())
async def enter_hash_menu(callback_query: CallbackQuery, state: FSMContext) -> Message:
    if await state.get_state() in HashMenuStates:
        await state.set_state(None)

    return await callback_query.message.edit_text(
        text=HASH_MENU_ENTER_TEXT,
        reply_markup=Keyboards.inline.hash_menu()
    )


@callback_router.callback_query(HashMenuCb.Hashes.filter())
async def handle_hash_selection(callback_query: CallbackQuery, state: FSMContext, callback_data: HashMenuCb.Hashes) -> Message:
    hash_type: str = callback_data.hash_type
    new_state: State = await HashMenuHelper.get_state_by_hash_type(hash_type)

    await StorageUtils.set_hash_type(state, hash_type)
    await state.set_state(new_state)
    await StorageUtils.set_message_id_to_delete(state, callback_query.message.message_id)

    return await callback_query.message.edit_text(
        text=HASH_SELECTION_TEXT,
        reply_markup=Keyboards.inline.return_to_hash_menu()
    )
