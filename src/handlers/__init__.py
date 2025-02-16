from aiogram import Router

from .hash_menu_handlers import hash_menu_router
from .pwd_mgr_handlers import password_manager_router
from .start_menu_handlers import start_menu_router

__all__ = "router"

handlers_router = Router()
handlers_router.include_routers(
    hash_menu_router,
    password_manager_router,
    start_menu_router
)
