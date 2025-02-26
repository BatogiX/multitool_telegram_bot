import secrets
import string
from utils import BotUtils

class GenerateRandomPasswordHelper:
    @classmethod
    def generate_password(cls, length: int = 16) -> str:
        alphabet: str = string.ascii_letters + string.digits + string.punctuation
        rand_pwd: str = ''.join(secrets.choice(alphabet) for _ in range(length))
        return BotUtils.escape_markdown_v2(rand_pwd)
