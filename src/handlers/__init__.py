from .gen_rand_pwd import gen_rand_pwd_router
from .hash_menu import hash_menu_router
from .pwd_mgr import password_manager_router
from .start_menu import start_menu_router

handler_routers = (
    start_menu_router,
    hash_menu_router,
    password_manager_router,
    gen_rand_pwd_router,
)

__all__ = ("handler_routers",)
