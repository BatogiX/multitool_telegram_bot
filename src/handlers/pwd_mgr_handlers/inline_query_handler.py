import hashlib

from aiogram import Router, F
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from config import db_manager
from keyboards import InlinePasswordManagerKeyboard

inline_query_router = Router(name=__name__)


@inline_query_router.inline_query(F.query.startswith("service="))
async def search(query: InlineQuery):
    search_text = query.query.replace("service=", "")

    services: list[str] = await db_manager.relational_db.inline_search_service(query.from_user.id, search_text)
    articles = [
        InlineQueryResultArticle(
            id=hashlib.md5(service.encode()).hexdigest(),
            title=service,
            input_message_content=InputTextMessageContent(message_text=f"🔎 {service}"),
            reply_markup=InlinePasswordManagerKeyboard.pwd_mgr_inline_search(service)
        ) for service in services
    ]

    await query.answer(articles, is_personal=True)