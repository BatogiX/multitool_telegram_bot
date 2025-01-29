from aiogram import Router

from .callback_handler import callback_router
from .command_handler import command_router
from .fsm_handler import fsm_router
from .message_handler import message_router

router = Router()

router.include_router(command_router)
router.include_router(callback_router)
router.include_router(fsm_router)
router.include_router(message_router)
