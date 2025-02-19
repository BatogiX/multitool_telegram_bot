from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.markdown import text

from .callback_handler import HASH_MENU_ENTER_TEXT
from keyboards import InlineKeyboards
from models.states import HashMenuStates
from utils import BotUtils
from helpers import HashMenuHelper

fsm_router = Router(name=__name__)


@fsm_router.message(StateFilter(HashMenuStates), F.document)
async def process_check_hash(message: Message, state: FSMContext):
    await state.set_state(None)
    await BotUtils.delete_fsm_message(state, message)

    try:
        is_match, expected_hash, hash_type, computed_hash = await HashMenuHelper.check_hash(state, message)
    except Exception as e:
        return await message.answer(
            text=f"{str(e)}\n\n{HASH_MENU_ENTER_TEXT}",
            reply_markup=InlineKeyboards.hash_menu()
        )

    status = "✅" if is_match else "❌"
    response_text = text(
        f"{status} Expected hash: {status}",
        f"`{expected_hash}`",
        f"{status} {hash_type} hash: {status}",
        f"`{computed_hash}`",
        sep="\n",
    )

    await message.answer(
        text=response_text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboards.return_to_hash_menu_or_retry(hash_type)
    )

