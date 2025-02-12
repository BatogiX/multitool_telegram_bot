from aiogram import Router

from .password_manager_cb_handler import callback_router
from .password_manager_fsm_handler import fsm_router

__all__ = "password_manager_router"

password_manager_router = Router()
password_manager_router.include_routers(
    callback_router,
    fsm_router
)


