from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BotConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8', extra="allow"
    )

    token: str = Field(default=..., alias="TOKEN")  # Required
    sep: str = " "

    @property
    def admins(self) -> frozenset[int] | frozenset[None]:
        """
        Retrieves the admin IDs as a frozenset of integers from the environment variable
        'ADMIN_IDS', which is a comma-separated string.
        """
        if self.ADMIN_IDS:
            return frozenset(int(admin_id) for admin_id in self.ADMIN_IDS.split(",") if admin_id.isdigit())
        return frozenset()


bot_config = BotConfig()
