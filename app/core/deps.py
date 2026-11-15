"""Dependency dùng chung trong router, chủ yếu là kiểm tra token.

Dùng OAuth2 của FastAPI làm đăng nhập thì /docs có nút Authorize tự động, nhưng
ở đây mình chỉ dùng HTTPBearer: FE gọi /api/auth/login để lấy token rồi gửi kèm
header "Authorization: Bearer <token>" cho các API cần đăng nhập.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User

# auto_error=False: tự trả 401 (thay vì 403 mặc định của FastAPI) khi thiếu token
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Lấy user đang đăng nhập từ token. Thiếu token / token sai / hết hạn -> 401."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Chưa gửi token, thêm header: Authorization: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ hoặc đã hết hạn, hãy đăng nhập lại",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.get(User, int(payload["sub"]))
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản không tồn tại hoặc đã bị khoá",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """Chỉ tài khoản admin (users.is_admin = 1) mới đi qua được.

    Chưa đăng nhập vẫn là 401 (do get_current_user), đã đăng nhập nhưng không phải
    admin thì 403. Dùng trong router:  admin: User = Depends(get_current_admin)
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ admin mới được thực hiện thao tác này",
        )
    return current_user
