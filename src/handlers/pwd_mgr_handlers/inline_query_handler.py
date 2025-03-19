from aiogram import Router, F
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from database import db_manager
from config import bot_cfg
from keyboards import Keyboards
from utils import InlineKeyboardsUtils as KbUtils, BotUtils

inline_query_router = Router(name=__name__)


@inline_query_router.inline_query(F.query.startswith(KbUtils.inline_query_search_service))
async def search(query: InlineQuery):
    search_text = query.query.replace(f"{KbUtils.inline_query_search_service}", "")

    services: list[str] = await db_manager.relational_db.inline_search_service(
        user_id=query.from_user.id,
        service=search_text,
        limit=bot_cfg.dynamic_buttons_limit
    )
    articles = [
        InlineQueryResultArticle(
            id=service,
            title=BotUtils.strip_protocol(service),
            input_message_content=InputTextMessageContent(message_text=f"🔎 {service}"),
            reply_markup=Keyboards.inline.pwd_mgr_inline_search(service)
        ) for service in services
    ]

    await query.answer(articles, is_personal=True)