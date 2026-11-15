"""Băm mật khẩu + tạo/kiểm tra token.

- Mật khẩu: băm bằng PBKDF2-SHA256 (thư viện chuẩn của Python, không cần cài thêm).
  Không bao giờ lưu mật khẩu gốc vào DB, chỉ lưu chuỗi băm.
- Token: JWT (thư viện PyJWT). FE gửi lên ở header: Authorization: Bearer <token>
"""
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings

# Số vòng băm: càng lớn càng khó dò mật khẩu, đổi lại chậm hơn 1 chút khi đăng nhập
_PBKDF2_ITERATIONS = 260_000


def hash_password(password: str) -> str:
    """Trả về chuỗi băm dạng: pbkdf2_sha256$<vòng lặp>$<salt>$<hash>"""
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), _PBKDF2_ITERATIONS
    )
    return f"pbkdf2_sha256${_PBKDF2_ITERATIONS}${salt}${digest.hex()}"


def verify_password(password: str, hashed: str) -> bool:
    """So sánh mật khẩu người dùng nhập với chuỗi băm trong DB."""
    try:
        algorithm, iterations, salt, expected = hashed.split("$")
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), int(iterations)
    )
    # compare_digest: so sánh không phụ thuộc thời gian -> chống dò từng ký tự
    return hmac.compare_digest(digest.hex(), expected)


def create_access_token(user_id: int, username: str) -> str:
    """Tạo token JWT có hạn dùng ACCESS_TOKEN_EXPIRE_MINUTES phút."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),  # chủ sở hữu token
        "username": username,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def decode_access_token(token: str) -> dict | None:
    """Giải mã token. Trả về None nếu token sai chữ ký hoặc hết hạn."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None
    if payload.get("type") != "access":
        return None
    return payload
