from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False)
    address_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    voucher_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    final_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)

    payment_method: Mapped[str | None] = mapped_column(
        String(50), nullable=True)
    payment_status: Mapped[str | None] = mapped_column(
        String(50), nullable=True)
    order_status: Mapped[str] = mapped_column(
        String(50), default="Chờ xác nhận")
    customer_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id"), nullable=False)
    food_id: Mapped[int] = mapped_column(
        ForeignKey("foods.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    total_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)

    order: Mapped["Order"] = relationship(back_populates="items")
