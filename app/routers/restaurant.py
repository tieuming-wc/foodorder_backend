"""API dành cho tài khoản nhà hàng (users.role = 'restaurant').

    GET /api/restaurant/orders              đơn được gán cho nhà hàng của tôi
    PUT /api/restaurant/orders/{id}/confirm  xác nhận đơn đang chờ duyệt

Nhà hàng chỉ thấy đơn có restaurant_id trùng với tài khoản trong token.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_restaurant
from app.crud import order as order_crud
from app.db.session import get_db
from app.models.order import ORDER_STATUSES, STATUS_LABELS
from app.models.user import User
from app.schemas.order import AdminOrderOut

router = APIRouter(
    prefix="/restaurant/orders",
    tags=["Restaurant - Orders"],
    dependencies=[Depends(get_current_restaurant)],
)


@router.get("", response_model=list[AdminOrderOut])
def list_my_restaurant_orders(
    status_filter: str | None = Query(
        default=None,
        alias="status",
        description="Lọc theo trạng thái: pending, confirmed, shipping, completed, cancelled",
    ),
    current_user: User = Depends(get_current_restaurant),
    db: Session = Depends(get_db),
):
    """Danh sách đơn của nhà hàng đang đăng nhập, mới nhất lên đầu."""
    if status_filter is not None and status_filter not in ORDER_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Trạng thái không hợp lệ, chọn một trong: {', '.join(ORDER_STATUSES)}",
        )
    return order_crud.get_restaurant_orders(db, current_user.id, status=status_filter)


@router.put("/{order_id}/confirm", response_model=AdminOrderOut)
def confirm_order(
    order_id: int,
    current_user: User = Depends(get_current_restaurant),
    db: Session = Depends(get_db),
):
    """Nhà hàng xác nhận đơn: pending -> confirmed (đơn sẵn sàng cho shipper nhận)."""
    order = order_crud.get_order(db, order_id)
    # Đơn của nhà hàng khác coi như không tồn tại (không lộ dữ liệu)
    if order is None or order.restaurant_id != current_user.id:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy đơn hàng id={order_id}")
    if order.status != "pending":
        raise HTTPException(
            status_code=400,
            detail=(
                f"Chỉ xác nhận được đơn đang "
                f"'{STATUS_LABELS.get('pending', 'pending')}', "
                f"đơn này đang '{STATUS_LABELS.get(order.status, order.status)}'"
            ),
        )

    order = order_crud.update_order_status(db, order, "confirmed")
    return AdminOrderOut.model_validate(order)
