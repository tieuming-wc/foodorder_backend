"""Model = cấu trúc 1 bảng trong MySQL. Bảng món ăn: items.

Mỗi món thuộc 1 danh mục (categories) và có thể có link ảnh mạng để FE hiển thị.
"""
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

if TYPE_CHECKING:  # chi de type hint, tranh import vong khi chay
    from app.models.category import Category


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    # Link ảnh trên mạng (http/https) để FE hiển thị món
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # Danh mục bị xoá thì món vẫn còn, chỉ mất danh mục
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # lazy="selectin": danh sách món lấy kèm danh mục trong 1 câu SQL phụ (không N+1)
    category: Mapped["Category | None"] = relationship(
        back_populates="items", lazy="selectin"
    )
