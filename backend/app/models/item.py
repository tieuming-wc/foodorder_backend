"""Model = cấu trúc 1 bảng trong MySQL. Bảng mẫu: items.

Khi làm đề tài, copy file này để tạo bảng của nhóm (vd: Product, Order, Movie...).
"""
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    category: Mapped[str] = mapped_column(String(100), default="Món chính")
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    delivery_time: Mapped[str] = mapped_column(String(50), default="25–35 phút")
    rating: Mapped[Decimal] = mapped_column(Numeric(3, 1), default=0)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
