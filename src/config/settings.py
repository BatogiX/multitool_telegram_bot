from pathlib import Path
from pydantic_settings import SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ENV = PROJECT_ROOT / ".env"


def base_settings_config(prefix: str) -> SettingsConfigDict:
    return SettingsConfigDict(
        env_prefix=prefix,
        env_file=DEFAULT_ENV,
        frozen=True,
        extra="ignore"
    )
