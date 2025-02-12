from aiogram import Router

from .start_menu_cmd_handler import command_router
from .start_menu_cb_handler import callback_router

start_menu_router = Router()

start_menu_router.include_router(command_router)
start_menu_router.include_router(callback_router)

__all__ = ['start_menu_router']
