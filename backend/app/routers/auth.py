import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    ALGORITHM,
    create_access_token,
    hash_password,
    verify_password,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    PasswordUpdate,
    TokenResponse,
    UserLogin,
    UserOut,
    UserRegister,
    UserUpdate,
)


router = APIRouter(prefix="/auth", tags=["Auth"])
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token không hợp lệ hoặc đã hết hạn.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise unauthorized

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.AUTH_SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        subject = payload.get("sub")
        if not subject:
            raise unauthorized
        user_id = int(subject)
    except (jwt.InvalidTokenError, TypeError, ValueError):
        raise unauthorized

    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise unauthorized

    return user


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(data: UserRegister, db: Session = Depends(get_db)):
    email = str(data.email).strip().lower()

    existing_user = db.scalar(
        select(User).where(func.lower(User.email) == email)
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email này đã được đăng ký.",
        )

    user = User(
        full_name=data.full_name.strip(),
        phone=data.phone.strip() if data.phone else None,
        email=email,
        hashed_password=hash_password(data.password),
        # Không nhận role từ client: đăng ký mới luôn là customer.
        role="customer",
        is_active=True,
    )

    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email này đã được đăng ký.",
        )

    db.refresh(user)

    return TokenResponse(
        access_token=create_access_token(user.id),
        user=user,
    )


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    email = str(data.email).strip().lower()
    user = db.scalar(
        select(User).where(func.lower(User.email) == email)
    )

    if (
        user is None
        or not user.is_active
        or not verify_password(data.password, user.hashed_password)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenResponse(
        access_token=create_access_token(user.id),
        user=user,
    )


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserOut)
def update_me(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    email = str(data.email).strip().lower()
    existing_user = db.scalar(
        select(User).where(
            func.lower(User.email) == email,
            User.id != current_user.id,
        )
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email này đã được tài khoản khác sử dụng.",
        )

    current_user.full_name = data.full_name.strip()
    current_user.phone = data.phone.strip() if data.phone else None
    current_user.email = email

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email này đã được tài khoản khác sử dụng.",
        )

    db.refresh(current_user)
    return current_user


@router.put("/me/password")
def update_password(
    data: PasswordUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu hiện tại không chính xác.",
        )

    if data.current_password == data.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu mới phải khác mật khẩu hiện tại.",
        )

    current_user.hashed_password = hash_password(data.new_password)
    db.commit()
    return {"message": "Đổi mật khẩu thành công."}


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    return {"message": "Đăng xuất thành công"}