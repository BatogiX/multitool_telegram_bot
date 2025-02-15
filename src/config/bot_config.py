from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self


class BotConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra="allow",
        env_prefix="BOT_"
    )

    token: str = ...
    admin_ids: str | frozenset[int] = ...
    sep: str = " "
    dynamic_buttons_limit: int = 16
    dynamical_buttons_per_row: int = 2

    @model_validator(mode="before")
    def _set_admin_ids(self) -> Self:
        admin_ids = self.get("admin_ids", "")
        self["admin_ids"] = frozenset(
            int(admin_id) for admin_id in admin_ids.split(",") if admin_id.isdigit()
        )
        return self


bot_config = BotConfig()
