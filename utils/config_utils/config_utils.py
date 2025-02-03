from urllib.parse import quote

from config import config as c


class ConfigUtils:
    @staticmethod
    def get_postgres_url():
        if c.RELATIONAL_DB_URL:
            return c.RELATIONAL_DB_URL
        auth_part = f"{quote(c.RELATIONAL_DB_USER)}:{quote(c.RELATIONAL_DB_PASSWORD)}@" if c.RELATIONAL_DB_PASSWORD else ""
        return f"postgres://{auth_part}{c.RELATIONAL_DB_HOST}:{c.RELATIONAL_DB_PORT}/{c.RELATIONAL_DB_NAME}"

    @staticmethod
    def get_redis_url():
        if c.KEY_VALUE_DB_URL:
            return c.KEY_VALUE_DB_URL
        auth_part = f"{quote(c.KEY_VALUE_DB_USERNAME)}:{quote(c.KEY_VALUE_DB_PASSWORD)}@" if c.KEY_VALUE_DB_PASSWORD else ""
        return f"redis://{auth_part}{c.KEY_VALUE_DB_HOST}:{c.KEY_VALUE_DB_PORT}"