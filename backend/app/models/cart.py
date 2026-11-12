"""Model giỏ hàng: mỗi user có đúng một giỏ (carts) và các món trong giỏ (cart_items).

Ràng buộc quan trọng:
- `carts.user_id` UNIQUE  -> một user chỉ có một giỏ.
- `cart_items` UNIQUE (cart_id, food_id) -> cùng một món không xuất hiện 2 dòng trong
  cùng một giỏ; muốn thêm nữa thì tăng `quantity` của dòng đã có.
- `quantity > 0` (CHECK) -> không lưu dòng có số lượng 0 hoặc âm.

Xóa giỏ sẽ xóa luôn các dòng của giỏ (cascade), không để lại dữ liệu mồ côi.
"""
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.food import Food  # noqa: F401 - để SQLAlchemy nối quan hệ cart_items.food


class Cart(Base):
    __tablename__ = "carts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # UNIQUE = mỗi user một giỏ; index để tra cứu giỏ theo user cho nhanh
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    items: Mapped[list["CartItem"]] = relationship(
        back_populates="cart",
        cascade="all, delete-orphan",
        order_by="CartItem.id",
    )


class CartItem(Base):
    __tablename__ = "cart_items"
    __table_args__ = (
        UniqueConstraint("cart_id", "food_id", name="uq_cart_items_cart_id_food_id"),
        CheckConstraint("quantity > 0", name="ck_cart_items_quantity_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cart_id: Mapped[int] = mapped_column(
        ForeignKey("carts.id", ondelete="CASCADE"), index=True
    )
    food_id: Mapped[int] = mapped_column(ForeignKey("foods.id"), index=True)
    quantity: Mapped[int] = mapped_column(default=1)

    cart: Mapped["Cart"] = relationship(back_populates="items")
    # lazy="joined": lấy kèm thông tin món trong cùng câu query, tránh N+1 khi trả giỏ
    food: Mapped["Food"] = relationship(lazy="joined")
