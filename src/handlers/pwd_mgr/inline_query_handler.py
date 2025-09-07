from aiogram import F, Router
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

import keyboards.inline
from database import db
from keyboards.buttons.pwd_mgr import INLINE_QUERY_SEARCH_SERVICE
from utils import add_protocol

inline_query_router = Router(name=__name__)


@inline_query_router.inline_query(F.query.startswith(INLINE_QUERY_SEARCH_SERVICE))
async def search(inline_query: InlineQuery):
    search_text = inline_query.query.replace(f"{INLINE_QUERY_SEARCH_SERVICE}", "")

    if not search_text:
        print(search_text)
        return

    services = await db.sql.inline_search_service(
        user_id=inline_query.from_user.id,
        service=search_text,
    )
    articles = [
        InlineQueryResultArticle(
            id=service,
            title=service,
            input_message_content=InputTextMessageContent(
                message_text=f"🔎 {add_protocol(service)}",
            ),
            reply_markup=keyboards.inline.pwd_mgr_inline_search_ikm(service),
        )
        for service in services
    ]

    await inline_query.answer(articles, is_personal=True)
