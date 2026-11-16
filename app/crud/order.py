"""CRUD = các hàm đọc/ghi DB cho bảng orders. Router gọi vào đây, không viết SQL trong router."""
from datetime import datetime

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.order import Order


def get_user_orders(db: Session, user_id: int, status: str | None = None) -> list[Order]:
    """Toàn bộ đơn hàng của 1 user, đơn mới nhất lên đầu.

    Sắp theo created_at giảm dần, thêm id giảm dần để hai đơn cùng thời điểm luôn
    ra cùng một thứ tự giữa các lần gọi.
    """
    query = (
        select(Order)
        .where(Order.user_id == user_id)
        .order_by(desc(Order.created_at), desc(Order.id))
    )
    if status:
        query = query.where(Order.status == status)
    return list(db.scalars(query))


def get_user_order(db: Session, user_id: int, order_id: int) -> Order | None:
    """Chỉ tìm trong đơn của chính user -> đơn của người khác coi như không tồn tại."""
    return db.scalar(
        select(Order).where(Order.id == order_id, Order.user_id == user_id)
    )


def cancel_order(db: Session, order: Order) -> Order:
    """Đổi trạng thái sang cancelled. Việc kiểm tra đơn có huỷ được hay không do router làm."""
    order.status = "cancelled"
    order.canceled_at = datetime.now()
    db.commit()
    db.refresh(order)
    return order
