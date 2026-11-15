"""Model = cấu trúc 1 bảng trong MySQL. Bảng đơn hàng: orders + order_items.

1 đơn hàng (orders) thuộc về 1 user và có nhiều dòng hàng (order_items).
Mỗi dòng hàng lưu lại tên + giá tại lúc mua để sau này item bị sửa/xoá thì
lịch sử mua hàng vẫn hiển thị đúng như lúc đặt.
"""
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

# Các trạng thái của 1 đơn hàng
# pending = Chờ duyệt, confirmed = Đã xác nhận, shipping = Đang giao,
# completed = Hoàn thành, cancelled = Đã huỷ
ORDER_STATUSES = ("pending", "confirmed", "shipping", "completed", "cancelled")
# Chỉ đơn còn "Chờ duyệt" mới được tự huỷ
CANCELABLE_STATUSES = ("pending",)


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # Chủ đơn hàng -> lịch sử mua hàng lọc theo cột này
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    canceled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # lazy="selectin": lấy luôn các dòng hàng của mọi đơn trong 1 câu SQL
    # (danh sách lịch sử mua hàng không bị N+1 query).
    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    @property
    def can_cancel(self) -> bool:
        return self.status in CANCELABLE_STATUSES


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), index=True
    )
    # Item gốc bị xoá thì đơn cũ vẫn giữ được tên + giá đã mua
    item_id: Mapped[int | None] = mapped_column(
        ForeignKey("items.id", ondelete="SET NULL"), nullable=True
    )
    item_name: Mapped[str] = mapped_column(String(255))
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    quantity: Mapped[int] = mapped_column(Integer, default=1)

    order: Mapped["Order"] = relationship(back_populates="items")

    @property
    def subtotal(self) -> Decimal:
        return self.unit_price * self.quantity
