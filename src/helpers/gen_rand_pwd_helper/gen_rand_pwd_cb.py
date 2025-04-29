import secrets
import string

from utils import escape_markdown_v2

ALPHABET = string.ascii_letters + string.digits + string.punctuation


def generate_password(length: int = 16) -> str:
    rand_pwd = ''.join(secrets.choice(ALPHABET) for _ in range(length))
    return escape_markdown_v2(rand_pwd)
