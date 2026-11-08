"""Đăng nhập: băm mật khẩu, tạo/kiểm tra token và dependency get_current_user.

Chỉ dùng thư viện chuẩn của Python (hashlib, hmac) nên không cần cài thêm gì.

Cách dùng trong router:

    current_user: User = Depends(get_current_user)

-> Request thiếu/sai token sẽ tự trả 401, code phía dưới chỉ chạy khi đã đăng nhập.
Task đăng nhập/đăng ký sau này dùng lại `hash_password`, `verify_password`
và `create_access_token` ở đây.
"""
import base64
import hashlib
import hmac
import json
import secrets
import time

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User

_PASSWORD_ITERATIONS = 200_000


# ---------------------------------------------------------------- mật khẩu
def hash_password(password: str) -> str:
    """Băm mật khẩu kèm muối (salt). Mỗi lần gọi cho ra chuỗi khác nhau."""
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt), _PASSWORD_ITERATIONS
    )
    return f"pbkdf2_sha256${_PASSWORD_ITERATIONS}${salt}${digest.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    """So mật khẩu người dùng nhập với chuỗi đã băm trong cột `users.password_hash`."""
    try:
        algorithm, iterations, salt, expected = password_hash.split("$")
        if algorithm != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), bytes.fromhex(salt), int(iterations)
        )
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(digest.hex(), expected)


# ------------------------------------------------------------------ token
def _b64encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _b64decode(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def _sign(body: str) -> str:
    signature = hmac.new(
        settings.SECRET_KEY.encode("utf-8"), body.encode("ascii"), hashlib.sha256
    ).digest()
    return _b64encode(signature)


def create_access_token(user_id: int) -> str:
    """Tạo token đăng nhập (payload ký bằng SECRET_KEY, có hạn sử dụng)."""
    now = int(time.time())
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }
    body = _b64encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    return f"{body}.{_sign(body)}"


def decode_access_token(token: str) -> int | None:
    """Trả về user_id nếu token đúng chữ ký và còn hạn, ngược lại trả None."""
    try:
        body, signature = token.split(".")
    except ValueError:
        return None
    if not hmac.compare_digest(_sign(body), signature):
        return None
    try:
        payload = json.loads(_b64decode(body))
        if int(payload["exp"]) < int(time.time()):
            return None
        return int(payload["sub"])
    except (ValueError, TypeError, KeyError):
        return None


# ------------------------------------------------------- dependency dùng lại
# auto_error=False để tự trả câu thông báo lỗi bằng tiếng Việt
bearer_scheme = HTTPBearer(auto_error=False, description="Bearer <access_token>")


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Lấy user đang đăng nhập từ header: Authorization: Bearer <token>."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Chưa đăng nhập. Gửi header: Authorization: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ hoặc đã hết hạn. Đăng nhập lại.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.get(User, user_id)
    if user is None or user.status != 1:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản không tồn tại hoặc đã bị khoá",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
