import base64
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings


ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
PBKDF2_ITERATIONS = 600_000


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )

    salt_text = base64.urlsafe_b64encode(salt).decode("ascii").rstrip("=")
    hash_text = base64.urlsafe_b64encode(password_hash).decode("ascii").rstrip("=")

    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt_text}${hash_text}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, iterations_text, salt_text, expected_hash_text = stored_hash.split("$")
        if algorithm != "pbkdf2_sha256":
            return False

        iterations = int(iterations_text)
        salt = base64.urlsafe_b64decode(salt_text + "=" * (-len(salt_text) % 4))
        expected_hash = base64.urlsafe_b64decode(
            expected_hash_text + "=" * (-len(expected_hash_text) % 4)
        )

        actual_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            iterations,
        )
        return hmac.compare_digest(actual_hash, expected_hash)
    except (ValueError, TypeError):
        return False


def create_access_token(user_id: int) -> str:
    secret_key = settings.AUTH_SECRET_KEY
    if len(secret_key) < 32:
        raise RuntimeError("AUTH_SECRET_KEY phải có ít nhất 32 ký tự.")

    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }

    return jwt.encode(payload, secret_key, algorithm=ALGORITHM)