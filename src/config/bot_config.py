import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class BotConfig(BaseSettings):
    model_config = SettingsConfigDict(
        extra="allow",
        env_prefix="BOT_",
    )

    token: str = ...
    admins: frozenset[int] = frozenset(int(id) for id in os.getenv("BOT_ADMIN_IDS", "").split(",") if id.isdigit())

    sep: str = " "
    dynamic_buttons_limit: int = 16
    dynamical_buttons_per_row: int = 2


bot_config = BotConfig()
print(bot_config.admins)
