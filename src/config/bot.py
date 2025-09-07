import secrets
from typing import ClassVar, Final, Literal, Self, final

from pydantic import AliasChoices, Field, model_validator
from pydantic_settings import BaseSettings

from utils.config import base_settings_config

MODE = Literal["polling", "webhook"]


@final
class BotConfig(BaseSettings):
    PREFIX: ClassVar[str] = "BOT_"
    model_config = base_settings_config(prefix=PREFIX)

    token: str = Field(default=...)  # Bot token mandatory attribute
    admins: set[int] = set()  # JSON list of admin user IDs, e.g., [123456789, 987654321]
    mode: MODE = "polling"
    sep: str = " "
    dynamic_buttons_limit: int = Field(default=16, ge=1)
    dynamical_buttons_per_row: int = Field(default=2, ge=1)
    ttl: int = Field(default=600, ge=1)

    # WEBHOOK
    web_server_url: str = ""
    web_server_host: str = "127.0.0.1"  # 0.0.0.0
    web_server_port: int = Field(
        default=8000,
        validation_alias=AliasChoices(
            "PORT",
            PREFIX + "WEB_SERVER_PORT",
        ),
    )
    webhook_path: str = ""  # "/webhook"
    webhook_secret: str = secrets.token_urlsafe(32)

    @model_validator(mode="after")
    def webhook(self) -> Self:
        if self.mode == "webhook" and not (self.webhook_path and self.webhook_secret and self.web_server_url):
            msg = "Error"
            raise ValueError(msg)
        return self


BOT_CFG: Final[BotConfig] = BotConfig()
