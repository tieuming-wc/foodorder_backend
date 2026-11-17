"""API quản lý đơn hàng dành cho admin. Đường dẫn đầy đủ:

    GET /api/admin/orders               danh sách đơn của TẤT CẢ khách + phân trang + lọc
    PUT /api/admin/orders/{id}/status   duyệt đơn / chuyển sang đang giao / hoàn thành / huỷ

Cả router đều bắt buộc token của tài khoản admin (users.is_admin = 1):
- chưa đăng nhập -> 401
- đã đăng nhập nhưng không phải admin -> 403

Response của cả 2 API đều trả đủ chi tiết: thông tin người đặt + danh sách món.
"""
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_admin
from app.crud import order as order_crud
from app.db.session import get_db
from app.models.order import ADMIN_TRANSITIONS, STATUS_LABELS
from app.models.user import User
from app.schemas.order import (
    AdminOrderListOut,
    AdminOrderOut,
    AdminOrderStatusUpdate,
)

router = APIRouter(
    prefix="/admin/orders",
    tags=["Admin - Orders"],
    # Gắn 1 lần cho cả router: mọi API bên dưới đều phải là admin
    dependencies=[Depends(get_current_admin)],
)

StatusFilter = Literal["pending", "confirmed", "shipping", "completed", "cancelled"]


@router.get("", response_model=AdminOrderListOut)
def list_all_orders(
    status_filter: StatusFilter | None = Query(
        default=None,
        alias="status",
        description="Lọc theo trạng thái: pending, confirmed, shipping, completed, cancelled",
    ),
    page: int = Query(default=1, ge=1, description="Trang hiện tại, bắt đầu từ 1"),
    limit: int = Query(default=20, ge=1, le=100, description="Số đơn mỗi trang"),
    db: Session = Depends(get_db),
):
    """Danh sách toàn bộ đơn của tất cả khách, mới nhất lên đầu."""
    total = order_crud.count_all_orders(db, status=status_filter)
    orders = order_crud.get_all_orders(
        db,
        status=status_filter,
        limit=limit,
        offset=(page - 1) * limit,
    )
    return AdminOrderListOut(
        total=total,
        page=page,
        limit=limit,
        total_pages=(total + limit - 1) // limit,
        items=[AdminOrderOut.model_validate(order) for order in orders],
    )


@router.put("/{order_id}/status", response_model=AdminOrderOut)
def update_order_status(
    order_id: int,
    data: AdminOrderStatusUpdate,
    db: Session = Depends(get_db),
):
    """Chuyển trạng thái đơn theo đúng luồng: pending -> confirmed -> shipping -> completed.

    Đơn đã huỷ / đã hoàn thành là trạng thái cuối nên không chuyển tiếp được.
    """
    order = order_crud.get_order(db, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy đơn hàng id={order_id}")

    current = order.status
    target = data.status

    if target == current:
        raise HTTPException(
            status_code=400,
            detail=f"Đơn hàng đang ở trạng thái '{STATUS_LABELS.get(current, current)}' rồi",
        )

    if target not in ADMIN_TRANSITIONS.get(current, ()):
        allowed = ADMIN_TRANSITIONS.get(current, ())
        if allowed:
            allowed_text = ", ".join(STATUS_LABELS.get(s, s) for s in allowed)
            detail = (
                f"Không thể chuyển từ '{STATUS_LABELS.get(current, current)}' "
                f"sang '{STATUS_LABELS.get(target, target)}'. "
                f"Chỉ được chuyển sang: {allowed_text}"
            )
        else:
            detail = (
                f"Đơn hàng đang '{STATUS_LABELS.get(current, current)}' "
                "là trạng thái cuối, không thể đổi trạng thái nữa"
            )
        raise HTTPException(status_code=400, detail=detail)

    order = order_crud.update_order_status(db, order, target)
    return AdminOrderOut.model_validate(order)
