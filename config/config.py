import os
from typing import Optional

from dotenv import load_dotenv

from db import DatabaseManager
from db.postgresql import PostgresqlManager
from db.redis import RedisManager

# ================================ #
# 🚀 LOADING ENVIRONMENT VARIABLES #
# ================================ #

load_dotenv()

# =============================== #
# 🔑 ADMIN IDS SEPERATED BY COMMA #
# =============================== #

ADMINS: set[int] = set(int(admin_id) for admin_id in os.getenv("ADMINS_IDS", "").split(","))

# ============ #
# 🤖 BOT TOKEN #
# ============ #

TOKEN: Optional[str] = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("Bot token is not set in environment variables.")

# =================================== #
# 🔥 KEY-VALUE DATABASE CONFIGURATION #
# =================================== #

class KeyValueDatabaseConfig:
    def __init__(self):
        self.host: str = os.getenv("KEY_VALUE_DB_HOST", "localhost")
        self.port: int = int(os.getenv("KEY_VALUE_DB_PORT", "6379"))
        self.username: Optional[str] = os.getenv("KEY_VALUE_DB_USERNAME")
        self.password: Optional[str] = os.getenv("KEY_VALUE_DB_PASSWORD")
        self.url: Optional[str] = os.getenv("KEY_VALUE_DB_URL")

key_value_db_config = KeyValueDatabaseConfig()

# ===================================== #
# 🛢️ RELATIONAL DATABASES CONFIGURATION #
# ===================================== #

class RelationalDatabaseConfig:
    def __init__(self):
        self.host: str = os.getenv("RELATIONAL_DB_HOST", "localhost")
        self.name: str = os.getenv("RELATIONAL_DB_NAME", "database")
        self.user: str = os.getenv("RELATIONAL_DB_USER", "user")
        self.port: int = int(os.getenv("RELATIONAL_DB_PORT", "5432"))
        self.password: Optional[str] = os.getenv("RELATIONAL_DB_PASSWORD")
        self.url: Optional[str] = os.getenv("DATABASE_URL")

relational_db_config = RelationalDatabaseConfig()

# ===================================== #
# ⚙️ DATABASE CONNECTION POOL SETTINGS #
# ===================================== #

class ConnectionPoolConfig:
    def __init__(self):
        # Key-value store (e.g., Redis, Memcached)
        self.key_value_max_pool_size: int = int(os.getenv("KEY_VALUE_DB_MAX_POOL_SIZE", 10))

        # Relational DB (e.g., PostgreSQL)
        self.relational_min_pool_size: int = int(os.getenv("RELATIONAL_DB_MIN_POOL_SIZE", 1))
        self.relational_max_pool_size: int = int(os.getenv("RELATIONAL_DB_MAX_POOL_SIZE", 10))
        self.relational_max_queries: int = int(os.getenv("RELATIONAL_DB_MAX_QUERIES", 1000))

connection_pool_config = ConnectionPoolConfig()

# ================================= #
# 🧰 DATABASE MANAGER INSTANTIATION #
# ================================= #

db_manager = DatabaseManager(
    key_value_db=RedisManager(),
    relational_db=PostgresqlManager()
)