import os

from dotenv import load_dotenv

ADMINS: set[int] = set()

load_dotenv()
TOKEN_ENV_VAR = os.getenv("TOKEN")
REDIS_HOST_ENV_VAR = os.getenv("REDIS_HOST")
REDIS_PORT_ENV_VAR = int(os.getenv("REDIS_PORT"))
REDIS_USERNAME_ENV_VAR =  os.getenv("REDIS_USERNAME", None)
REDIS_PASSWORD_ENV_VAR = os.getenv("REDIS_PASSWORD", None)
