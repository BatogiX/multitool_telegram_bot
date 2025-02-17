from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import CallbackQuery

from keyboards import InlineKeyboards
from models.callback_data import HashMenuCallbackData
from models.fsm_states import HashMenuStates
from utils.filters import CbMagicFilters
from utils.storage_utils import StorageUtils
from utils.hash_menu_utils import HashMenuUtils

callback_router = Router(name=__name__)

HASH_MENU_ENTER_TEXT = "Choose hash option"
HASH_SELECTION_TEXT = "Upload file and enter expected output in caption"

@callback_router.callback_query(CbMagicFilters.HashMenu_ENTER(F.data))
async def enter_hash_menu(callback_query: CallbackQuery, state: FSMContext):
    if await state.get_state() in HashMenuStates:
        await state.set_state(None)

    inline_kb = InlineKeyboards.hash_menu_keyboard()
    await callback_query.message.edit_text(text=HASH_MENU_ENTER_TEXT, reply_markup=inline_kb)


@callback_router.callback_query(HashMenuCallbackData.filter())
async def handle_hash_selection(callback_query: CallbackQuery, state: FSMContext, callback_data: HashMenuCallbackData):
    hash_type: str = callback_data.action
    new_state: State = await HashMenuUtils.get_state_by_hash_type(hash_type)

    await StorageUtils.set_hash_type(state, hash_type)
    await state.set_state(new_state)
    await StorageUtils.set_message_to_delete(state, callback_query.message.message_id)

    await callback_query.message.edit_text(
        text=HASH_SELECTION_TEXT,
        reply_markup=InlineKeyboards.return_to_hash_menu_keyboard()
    )
