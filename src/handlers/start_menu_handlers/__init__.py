from aiogram import Router

from .callback_handler import callback_router
from .command_handler import command_router

start_menu_router = Router()
start_menu_router.include_routers(
    command_router,
    callback_router
)

__all__ = "start_menu_router"
