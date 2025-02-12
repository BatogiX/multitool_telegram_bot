from aiogram import Router

from .hash_menu_cb_handler import callback_router
from .hash_menu_fsm_handler import fsm_router

hash_menu_router = Router()

hash_menu_router.include_routers(callback_router, fsm_router)

__all__ = ["hash_menu_router"]
