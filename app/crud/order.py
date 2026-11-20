"""CRUD = các hàm đọc/ghi DB cho bảng orders. Router gọi vào đây, không viết SQL trong router."""
from datetime import datetime
from decimal import Decimal

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.models.cart import CartItem
from app.models.order import Order, OrderItem


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


def checkout_cart(
    db: Session,
    user_id: int,
    cart_items: list[CartItem],
    note: str | None = None,
) -> Order:
    """Tạo đơn từ giỏ hàng VÀ xoá sạch giỏ trong CÙNG 1 transaction.

    - Mỗi dòng giỏ thành 1 dòng order_items, chốt lại tên + giá tại lúc mua.
    - total_amount tính từ giá hiện tại của món (không tin giá FE gửi lên).
    - Chỉ commit 1 lần ở cuối: nếu tạo đơn lỗi thì giỏ hàng còn nguyên, không bị
      mất món mà cũng không có đơn (tránh 2 thao tác lệch nhau).
    """
    order = Order(user_id=user_id, status="pending", note=note, total_amount=Decimal("0"))
    total = Decimal("0")
    for cart_item in cart_items:
        item = cart_item.item  # lazy="selectin" -> đã có sẵn, không query thêm
        total += item.price * cart_item.quantity
        order.items.append(
            OrderItem(
                item_id=item.id,
                item_name=item.name,
                unit_price=item.price,
                quantity=cart_item.quantity,
            )
        )
        db.delete(cart_item)  # dọn giỏ: xoá các món vừa đặt

    order.total_amount = total
    db.add(order)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(order)
    return order


def cancel_order(db: Session, order: Order) -> Order:
    """Đổi trạng thái sang cancelled. Việc kiểm tra đơn có huỷ được hay không do router làm."""
    order.status = "cancelled"
    order.canceled_at = datetime.now()
    db.commit()
    db.refresh(order)
    return order
