import os
from dotenv import load_dotenv

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

# ================= #
# 🔥 REDIS SETTINGS #
# ================= #

REDIS_HOST_ENV_VAR = os.getenv("REDIS_HOST")
REDIS_PORT_ENV_VAR = int(os.getenv("REDIS_PORT"))
REDIS_USERNAME_ENV_VAR = os.getenv("REDIS_USERNAME", None)
REDIS_PASSWORD_ENV_VAR = os.getenv("REDIS_PASSWORD", None)

# ====================== #
# 🛢️ POSTGRESQL SETTINGS #
# ====================== #

POSTGRESQL_HOST_ENV_VAR = os.getenv("POSTGRESQL_HOST")
POSTGRESQL_DATABASE_ENV_VAR = os.getenv("POSTGRESQL_DATABASE")
POSTGRESQL_USER_ENV_VAR = os.getenv("POSTGRESQL_USER", "postgres")
POSTGRESQL_PORT_ENV_VAR = os.getenv("POSTGRESQL_PORT")
POSTGRESQL_PASSWORD_ENV_VAR = os.getenv("POSTGRESQL_PASSWORD")
POSTGRESQL_URI_ENV_VAR = os.getenv("POSTGRESQL_URI")

# ================================ #
# ⚙️ CONNECTION POOL CONFIGURATION #
# ================================ #

# For key-value storage (Redis, Memcached, etc.)
KEY_VALUE_DB_MAX_POOL_SIZE = 10

# For relational database (PostgreSQL)
RELATION_DB_MIN_POOL_SIZE = 1
RELATION_DB_MAX_POOL_SIZE = 10
RELATION_DB_MAX_QUERIES = 1000
