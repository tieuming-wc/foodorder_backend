"""API đơn hàng của user đang đăng nhập. Đường dẫn đầy đủ:

    GET /api/orders/me                  toàn bộ đơn đã đặt, mới nhất lên đầu
    PUT /api/orders/{order_id}/cancel   tự huỷ đơn của chính mình

Cả hai API đều bắt buộc gửi token: Authorization: Bearer <access_token>

Quy tắc quan trọng:
- Mỗi user chỉ thấy / chỉ huỷ được đơn có user_id trùng với user trong token.
  Đơn của người khác trả 404 (không lộ đơn đó có thật hay không).
- Chỉ đơn đang "pending" (Chờ duyệt) mới được huỷ. Đơn "shipping" (Đang giao),
  "completed" (Hoàn thành) hay "confirmed" (Đã xác nhận) đều bị chặn với 400.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.crud import order as order_crud
from app.db.session import get_db
from app.models.order import ORDER_STATUSES, Order
from app.models.user import User
from app.schemas.order import CancelOrderOut, OrderOut

router = APIRouter(prefix="/orders", tags=["Orders"])

# Thông báo lỗi riêng cho từng trạng thái, để FE hiển thị dễ hiểu
_CANNOT_CANCEL_REASON = {
    "confirmed": "Đơn hàng đã được xác nhận nên không thể huỷ",
    "shipping": "Đơn hàng đang giao nên không thể huỷ",
    "completed": "Đơn hàng đã hoàn thành nên không thể huỷ",
    "cancelled": "Đơn hàng này đã bị huỷ trước đó",
}


@router.get("/me", response_model=list[OrderOut])
def list_my_orders(
    status_filter: str | None = Query(
        default=None,
        alias="status",
        description="Lọc theo trạng thái: pending, confirmed, shipping, completed, cancelled",
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Toàn bộ đơn hàng của user đang đăng nhập, đơn mới nhất lên đầu."""
    if status_filter is not None and status_filter not in ORDER_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Trạng thái không hợp lệ, chọn một trong: {', '.join(ORDER_STATUSES)}",
        )
    return order_crud.get_user_orders(db, current_user.id, status=status_filter)


@router.put("/{order_id}/cancel", response_model=CancelOrderOut)
def cancel_my_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Huỷ đơn của chính mình khi đơn còn "Chờ duyệt" (pending)."""
    # Lọc luôn theo user_id -> đơn của người khác coi như không tồn tại
    order: Order | None = order_crud.get_user_order(db, current_user.id, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy đơn hàng id={order_id}")

    if not order.can_cancel:
        raise HTTPException(
            status_code=400,
            detail=_CANNOT_CANCEL_REASON.get(
                order.status, f"Đơn hàng đang ở trạng thái '{order.status}' nên không thể huỷ"
            ),
        )

    order = order_crud.cancel_order(db, order)
    return CancelOrderOut(message=f"Đã huỷ đơn hàng #{order.id}", order=order)
