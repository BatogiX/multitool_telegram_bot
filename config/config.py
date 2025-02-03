import os
from dotenv import load_dotenv

from utils.config_utils import ConfigUtils

# ================================ #
# 🚀 LOADING ENVIRONMENT VARIABLES #
# ================================ #

load_dotenv()

# ============ #
# 🔑 ADMIN_IDS #
# ============ #

ADMINS: set[int] = set()

# ============ #
# 🤖 BOT TOKEN #
# ============ #

TOKEN_ENV_VAR = os.getenv("TOKEN")

# =============================== #
# 🔥 KEY-VALUE DATABASES SETTINGS #
# =============================== #

KEY_VALUE_DB_HOST = os.getenv("KEY_VALUE_DB_HOST", "localhost")
KEY_VALUE_DB_PORT = int(os.getenv("KEY_VALUE_DB_PORT", "6379"))
KEY_VALUE_DB_USERNAME = os.getenv("KEY_VALUE_DB_USERNAME")
KEY_VALUE_DB_PASSWORD = os.getenv("KEY_VALUE_DB_PASSWORD")
KEY_VALUE_DB_URL = os.getenv("KEY_VALUE_DB_URL")

# ================================ #
# 🛢️ RELATIONAL DATABASES SETTINGS #
# ================================ #

RELATIONAL_DB_HOST = os.getenv("RELATIONAL_DB_HOST", "localhost")
RELATIONAL_DB_NAME = os.getenv("RELATIONAL_DB_NAME", "database")
RELATIONAL_DB_USER = os.getenv("RELATIONAL_DB_USER", "user")
RELATIONAL_DB_PORT = int(os.getenv("RELATIONAL_DB_PORT", "5432"))
RELATIONAL_DB_PASSWORD = os.getenv("RELATIONAL_DB_PASSWORD")
RELATIONAL_DB_URL = os.getenv("DATABASE_URL")

# ================================ #
# ⚙️ CONNECTION POOL CONFIGURATION #
# ================================ #

# For key-value storage (Redis, Memcached, etc.)
KEY_VALUE_DB_MAX_POOL_SIZE = 10

# For relational database (PostgreSQL)
RELATIONAL_DB_MIN_POOL_SIZE = 1
RELATIONAL_DB_MAX_POOL_SIZE = 10
RELATIONAL_DB_MAX_QUERIES = 1000

# ================================ #
# 🛢️ DATABASE URLS                #
# ================================ #

PG_DB_URL = ConfigUtils.get_postgres_url()
REDIS_DB_URL = ConfigUtils.get_redis_url()