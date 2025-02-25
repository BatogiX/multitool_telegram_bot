from aiogram import Router

from .callback_handler import callback_router

gen_rand_pwd_router = Router()
gen_rand_pwd_router.include_routers(callback_router)

__all__ = "gen_rand_pwd_router"
