from aiogram import Router

from .password_manager_cb_handler import password_manager_cb_router

password_manager_router = Router()

password_manager_router.include_routers(password_manager_cb_router)

__all__ = ["password_manager_router"]