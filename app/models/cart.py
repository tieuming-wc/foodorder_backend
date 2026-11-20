"""Model = cấu trúc 1 bảng trong MySQL. Bảng giỏ hàng: cart_items.

Mỗi dòng = 1 món trong giỏ của 1 user. Một user chỉ có tối đa 1 dòng cho mỗi món
(ràng buộc uq_cart_user_item) -> thêm lại món đã có thì tăng quantity.

Khi đặt hàng thành công (POST /api/orders/checkout), các dòng giỏ của user bị xoá
trong CÙNG transaction với việc tạo đơn (xem app/crud/order.py: checkout_cart).
"""
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

if TYPE_CHECKING:  # chi de type hint, tranh import vong khi chay
    from app.models.item import Item


class CartItem(Base):
    __tablename__ = "cart_items"
    __table_args__ = (
        UniqueConstraint("user_id", "item_id", name="uq_cart_user_item"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # Giỏ của ai -> mọi query đều lọc theo cột này
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    # Món được thêm. Món bị xoá khỏi thực đơn thì dòng giỏ cũng mất.
    item_id: Mapped[int] = mapped_column(
        ForeignKey("items.id", ondelete="CASCADE"), index=True
    )
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # lazy="selectin": lấy luôn thông tin món (tên, giá, ảnh) trong 1 câu SQL phụ,
    # danh sách giỏ hàng không bị N+1 query.
    item: Mapped["Item"] = relationship(lazy="selectin")

    @property
    def subtotal(self) -> Decimal:
        return self.item.price * self.quantity
