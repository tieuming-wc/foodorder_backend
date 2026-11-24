"""Model món ăn (bảng foods).

Bảng này là **bảng phụ thuộc** của giỏ hàng: `cart_items.food_id` trỏ tới `foods.id`.
Cột bám theo `docs/erd/README.md` (bảng `items` trong base chỉ là bảng mẫu).

Lưu ý: `category_id` chưa đặt khóa ngoại vì bảng `categories` chưa có trong repo;
khi task danh mục được merge thì thêm `ForeignKey("categories.id")`.
"""
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Food(Base):
    __tablename__ = "foods"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category_id: Mapped[int | None] = mapped_column(nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(150))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    stock: Mapped[int] = mapped_column(default=0)
    image_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
