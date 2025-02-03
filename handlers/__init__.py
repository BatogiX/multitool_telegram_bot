from aiogram import Router

from handlers.command_handler import command_router
from .hash_menu_handlers import hash_menu_router
from .message_handler import message_router
from .password_manager_handlers import password_manager_router

router = Router()

router.include_routers(hash_menu_router, password_manager_router, command_router, message_router)

__all__ = ["router"]
