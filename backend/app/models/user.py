"""Model người dùng (bảng users).

Bảng này là **bảng phụ thuộc** của giỏ hàng: `carts.user_id` trỏ tới `users.id` và có
UNIQUE để bảo đảm mỗi user chỉ có đúng một giỏ.

Repo hiện chưa có model người dùng nên ở đây khai báo tối thiểu, bám đúng cột trong
`docs/erd/README.md`. Task người dùng / đăng nhập sau này có thể bổ sung cột và nghiệp vụ.
"""
from datetime import datetime

from sqlalchemy import DateTime, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    role: Mapped[str] = mapped_column(String(20), default="customer")
    # 1 = đang hoạt động, 0 = bị khoá (ERD ghi TINYINT)
    status: Mapped[int] = mapped_column(SmallInteger, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
