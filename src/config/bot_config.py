import os

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class BotConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="BOT_", frozen=True)

    # Bot token mandatory attribute
    token: str

    # Set of admin ids (must be separated by comma)
    admins: set[int]

    sep: str = " "
    dynamic_buttons_limit: int = Field(default=16, ge=1)
    dynamical_buttons_per_row: int = Field(default=2, ge=1)
    ttl: int = Field(default=600, ge=1)

    @staticmethod
    def _parse_admins(admin_ids: str) -> set[int]:
        return {int(admin_ds) for admin_ds in admin_ids.split(",") if admin_ds.isdigit()}

    def __init__(self, **kwargs):
        admin_ids = os.getenv(f"{self.model_config['env_prefix']}ADMIN_IDS", "")
        kwargs["admins"] = self._parse_admins(admin_ids)
        super().__init__(**kwargs)


bot_cfg = BotConfig()
