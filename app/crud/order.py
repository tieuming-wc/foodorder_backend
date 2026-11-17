"""CRUD = các hàm đọc/ghi DB cho bảng orders. Router gọi vào đây, không viết SQL trong router."""
from datetime import datetime

from sqlalchemy import desc, func, select
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


def count_all_orders(db: Session, status: str | None = None) -> int:
    """Tổng số đơn của tất cả khách (để tính số trang)."""
    query = select(func.count()).select_from(Order)
    if status:
        query = query.where(Order.status == status)
    return db.scalar(query) or 0


def get_all_orders(
    db: Session,
    status: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[Order]:
    """Danh sách đơn của mọi khách cho admin, mới nhất lên đầu.

    items + user dùng lazy="selectin" nên chỉ tốn 1 câu SQL phụ cho mỗi quan hệ,
    không bị N+1 khi hiển thị cả bảng.
    """
    query = (
        select(Order)
        .order_by(desc(Order.created_at), desc(Order.id))
        .limit(limit)
        .offset(offset)
    )
    if status:
        query = query.where(Order.status == status)
    return list(db.scalars(query))


def get_order(db: Session, order_id: int) -> Order | None:
    """Tìm 1 đơn bất kỳ (admin xem/sửa đơn của mọi khách)."""
    return db.get(Order, order_id)


def update_order_status(db: Session, order: Order, new_status: str) -> Order:
    """Ghi trạng thái mới. Việc kiểm tra luồng trạng thái do router làm."""
    order.status = new_status
    order.canceled_at = datetime.now() if new_status == "cancelled" else None
    db.commit()
    db.refresh(order)
    return order


def cancel_order(db: Session, order: Order) -> Order:
    """Đổi trạng thái sang cancelled. Việc kiểm tra đơn có huỷ được hay không do router làm."""
    order.status = "cancelled"
    order.canceled_at = datetime.now()
    db.commit()
    db.refresh(order)
    return order
