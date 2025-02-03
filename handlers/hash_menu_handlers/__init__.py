from aiogram import Router

from .hash_menu_cb_handler import hash_menu_cb_router
from .hash_menu_fsm_handler import fsm_router

hash_menu_router = Router()

hash_menu_router.include_routers(hash_menu_cb_router, fsm_router)

__all__ = ["hash_menu_router"]