from aiogram import Router

from .callback_handler import callback_router
from .fsm_handler import fsm_router

hash_menu_router = Router()
hash_menu_router.include_routers(
    callback_router,
    fsm_router
)

__all__ = "hash_menu_router"
