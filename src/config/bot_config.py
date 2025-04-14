import os

from pydantic_settings import BaseSettings
from pydantic import Field, AliasChoices

from config.settings import base_settings_config


class BotConfig(BaseSettings):
    model_config = base_settings_config(prefix="BOT_")

    token: str = ""           # Bot token mandatory attribute
    admins: set[int] = set()  # JSON list of admin user IDs, e.g., [123456789, 987654321]
    sep: str = " "
    dynamic_buttons_limit: int = Field(default=16, ge=1)
    dynamical_buttons_per_row: int = Field(default=2, ge=1)
    ttl: int = Field(default=600, ge=1)

    # WEBHOOK
    web_server_host: str = "0.0.0.0"
    web_server_port: int = Field(
        default=8080,
        validation_alias=AliasChoices(
            "PORT",
            model_config.get("env_prefix") + "WEB_SERVER_PORT"
        )
    )
    webhook_path: str = "/webhook"
    webhook_secret: str = os.urandom(32).hex()
    webhook_url: str = ""

bot_cfg: BotConfig = BotConfig()
