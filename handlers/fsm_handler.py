from aiogram import Router, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import text

from fsm import HashMenuStates
from keyboards import InlineKeyboards
from utils import HashMenuUtils, BotUtils

fsm_router = Router(name=__name__)


@fsm_router.message(StateFilter(HashMenuStates), F.document)
async def process_check_hash(message: types.Message, state: FSMContext):
    try:
        is_match, expected_hash, hash_type, computed_hash  = await HashMenuUtils.check_hash(state, message)
    except Exception as e:
        await message.answer(str(e))
    else:
        status = "✅" if is_match else "❌"
        response_text = text(
            f"{status} Expected hash: {status}",
            f"`{expected_hash}`",
            f"{status} {hash_type} hash: {status}",
            f"`{computed_hash}`",
            sep="\n",
        )
        inline_kb = InlineKeyboards.return_to_hash_menu_or_retry_keyboard(hash_type)
        await message.answer(response_text, parse_mode="Markdown", reply_markup=inline_kb)
        await BotUtils.delete_fsm_message(state, message)
