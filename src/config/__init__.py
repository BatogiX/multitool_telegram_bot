from dotenv import load_dotenv

load_dotenv()

from .bot_config import BotConfig
from .crypto_config import CryptographyConfig
from .db_config import RelationalDatabaseConfig, KeyValueDatabaseConfig
from database import DatabaseManager

bot_cfg = BotConfig()
crypto_cfg = CryptographyConfig()
relational_database_cfg = RelationalDatabaseConfig()
key_value_db_cfg = KeyValueDatabaseConfig()
db_manager = DatabaseManager(
    key_value_db_backend=key_value_db_cfg.backend,
    relational_db_backend=relational_database_cfg.backend
)

__all__ = (
    "bot_cfg",
    "db_manager",
    "crypto_cfg",
    "relational_database_cfg",
    "key_value_db_cfg",
)
