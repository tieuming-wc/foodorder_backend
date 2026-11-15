"""Model = cấu trúc 1 bảng trong MySQL. Bảng tài khoản: users."""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    # Không lưu mật khẩu gốc, chỉ lưu chuỗi băm (xem app/core/security.py)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    # False = khoá tài khoản, token cũ cũng không dùng được nữa
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # True = admin: được thêm/sửa/xoá dữ liệu dùng chung (vd bảng items)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
