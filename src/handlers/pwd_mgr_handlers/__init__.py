from aiogram import Router

from .callback_handler import callback_router
from .fsm_handler import fsm_router
from .inline_query_handler import inline_query_router

password_manager_router = Router()
password_manager_router.include_routers(
    callback_router,
    fsm_router,
    inline_query_router
)

__all__ = "password_manager_router"
