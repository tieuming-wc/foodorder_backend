"""CRUD = các hàm đọc/ghi DB cho bảng users."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import ROLE_CUSTOMER, User
from app.schemas.user import UserRegister


def get_user(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.scalar(select(User).where(User.username == username))


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def list_users(db: Session, role: str | None = None) -> list[User]:
    """Danh sách tài khoản cho trang admin, lọc theo vai trò nếu có."""
    query = select(User).order_by(User.id)
    if role:
        query = query.where(User.role == role)
    return list(db.scalars(query))


def create_user(db: Session, data: UserRegister) -> User:
    user = User(
        username=data.username,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
        email=data.email,
        # Tự đăng ký luôn là khách hàng; admin/nhà hàng/shipper do seed hoặc admin tạo
        role=ROLE_CUSTOMER,
    )
    db.add(user)
    db.commit()
    db.refresh(user)  # lấy lại id, created_at... do MySQL sinh ra
    return user
