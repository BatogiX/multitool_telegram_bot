from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

sep = " "

class BotConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra="allow")

    token: str = Field(default=..., alias="TOKEN") # Required
    admin_ids_str: str = Field(default="", alias="ADMIN_IDS")

    @property
    def admin_ids(self) -> frozenset[int]:
        if self.admin_ids_str:
            return frozenset(int(admin_id) for admin_id in self.admin_ids_str.split(",") if admin_id.isdigit())
        return frozenset()

    SEP: str = " "


bot_config = BotConfig()
