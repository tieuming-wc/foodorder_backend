from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DECIMAL, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base  # Hoặc đường dẫn Base tùy theo project của bạn

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    recipient_name = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=False)
    address_line = Column(Text, nullable=False)
    total_amount = Column(DECIMAL(10, 2), nullable=False)     # Tạm tính
    shipping_fee = Column(DECIMAL(10, 2), default=0.00)       # Phí ship
    discount_amount = Column(DECIMAL(10, 2), default=0.00)    # Giảm giá
    final_amount = Column(DECIMAL(10, 2), nullable=False)     # Tổng tiền
    order_status = Column(String(50), nullable=False, default="CHO_DUYET") # CHO_DUYET, DA_XAC_NHAN, DANG_GIAO, HOAN_THANH, DA_HUY
    customer_note = Column(Text, nullable=True)               # Ghi chú
    created_at = Column(DateTime, default=datetime.utcnow)

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    food_id = Column(Integer, nullable=False)
    food_name = Column(String(255), nullable=False)           # Tên món tại thời điểm đặt
    price = Column(DECIMAL(10, 2), nullable=False)            # Đơn giá tại thời điểm đặt
    quantity = Column(Integer, nullable=False)                # Số lượng

    order = relationship("Order", back_populates="items")