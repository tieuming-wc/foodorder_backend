"""Model = cấu trúc 1 bảng trong MySQL. Bảng danh mục món ăn: categories.

1 danh mục có nhiều món (items.category_id). Xoá danh mục thì các món vẫn còn,
chỉ mất liên kết danh mục (ON DELETE SET NULL).
"""
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

if TYPE_CHECKING:  # chi de type hint, tranh import vong khi chay
    from app.models.item import Item


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Số càng nhỏ càng đứng trước khi FE hiển thị danh mục
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    items: Mapped[list["Item"]] = relationship(back_populates="category")
