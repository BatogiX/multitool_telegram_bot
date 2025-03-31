from aiogram import Router, F
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from database import db_manager
from config import bot_cfg
from keyboards import Keyboards
from utils import InlineKeyboardsUtils as KbUtils, BotUtils

inline_query_router = Router(name=__name__)


@inline_query_router.inline_query(F.query.startswith(KbUtils.inline_query_search_service))
async def search(inline_query: InlineQuery):
    search_text = inline_query.query.replace(f"{KbUtils.inline_query_search_service}", "")

    if not search_text:
        print(search_text)
        return

    services: list[str] = await db_manager.relational_db.inline_search_service(user_id=inline_query.from_user.id, service=search_text)
    articles = [
        InlineQueryResultArticle(
            id=service,
            title=service,
            input_message_content=InputTextMessageContent(message_text=f"🔎 {BotUtils.add_protocol(service)}"),
            reply_markup=Keyboards.inline.pwd_mgr_inline_search(service)
        ) for service in services
    ]

    await inline_query.answer(articles, is_personal=True)
