"""API tài khoản. Đường dẫn đầy đủ:

    POST /api/auth/register   đăng ký tài khoản
    POST /api/auth/login      đăng nhập -> trả về token
    GET  /api/auth/me         xem thông tin của mình (cần gửi token)

Cách dùng token từ FE (không dùng OAuth2):
    1. POST /api/auth/login  {"username": "...", "password": "..."}
    2. Nhận {"access_token": "...", "token_type": "bearer", ...}, lưu lại
    3. Mỗi request cần đăng nhập, gửi header:
         Authorization: Bearer <access_token>
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_current_user
from app.core.security import create_access_token, verify_password
from app.crud import user as user_crud
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import TokenOut, UserLogin, UserOut, UserRegister

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: UserRegister, db: Session = Depends(get_db)):
    if user_crud.get_user_by_username(db, data.username) is not None:
        raise HTTPException(status_code=400, detail=f"Tên đăng nhập '{data.username}' đã có người dùng")
    if data.email and user_crud.get_user_by_email(db, data.email) is not None:
        raise HTTPException(status_code=400, detail=f"Email '{data.email}' đã được đăng ký")
    return user_crud.create_user(db, data)


@router.post("/login", response_model=TokenOut)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = user_crud.get_user_by_username(db, data.username)
    # Báo chung 1 câu cho cả 2 trường hợp sai tên và sai mật khẩu, tránh lộ tài khoản nào có thật
    if user is None or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sai tên đăng nhập hoặc mật khẩu",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tài khoản đã bị khoá")

    return TokenOut(
        access_token=create_access_token(user.id, user.username),
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserOut.model_validate(user),
    )


@router.get("/me", response_model=UserOut)
def read_me(current_user: User = Depends(get_current_user)):
    """Ví dụ 1 API bắt buộc đăng nhập. API khác muốn bảo vệ thì thêm:
        user: User = Depends(get_current_user)
    """
    return current_user
