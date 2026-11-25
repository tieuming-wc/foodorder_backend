"""API dành cho tài khoản shipper (users.role = 'shipper').

    GET /api/shipper/orders/available      đơn đã xác nhận, chưa ai nhận giao
    GET /api/shipper/orders/mine           đơn tôi đã nhận (đang giao + đã giao)
    PUT /api/shipper/orders/{id}/accept    nhận giao đơn (confirmed -> shipping)
    PUT /api/shipper/orders/{id}/delivered báo đã giao (shipping -> completed)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_shipper
from app.crud import order as order_crud
from app.db.session import get_db
from app.models.user import User
from app.schemas.order import AdminOrderOut

router = APIRouter(
    prefix="/shipper/orders",
    tags=["Shipper - Orders"],
    dependencies=[Depends(get_current_shipper)],
)


@router.get("/available", response_model=list[AdminOrderOut])
def list_available_orders(
    current_user: User = Depends(get_current_shipper),
    db: Session = Depends(get_db),
):
    """Đơn nhà hàng đã xác nhận và chưa có shipper nào nhận."""
    return order_crud.get_available_deliveries(db)


@router.get("/mine", response_model=list[AdminOrderOut])
def list_my_deliveries(
    current_user: User = Depends(get_current_shipper),
    db: Session = Depends(get_db),
):
    """Đơn shipper đang đăng nhập đã nhận, mới nhất lên đầu."""
    return order_crud.get_shipper_orders(db, current_user.id)


@router.put("/{order_id}/accept", response_model=AdminOrderOut)
def accept_order(
    order_id: int,
    current_user: User = Depends(get_current_shipper),
    db: Session = Depends(get_db),
):
    """Nhận giao: chỉ nhận được đơn đã xác nhận và chưa ai nhận."""
    order = order_crud.get_order(db, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy đơn hàng id={order_id}")
    if order.status != "confirmed":
        raise HTTPException(
            status_code=400,
            detail="Chỉ nhận được đơn đã xác nhận (confirmed)",
        )
    if order.shipper_id is not None:
        raise HTTPException(status_code=400, detail="Đơn này đã có shipper khác nhận")

    order = order_crud.accept_delivery(db, order, current_user.id)
    return AdminOrderOut.model_validate(order)


@router.put("/{order_id}/delivered", response_model=AdminOrderOut)
def mark_delivered(
    order_id: int,
    current_user: User = Depends(get_current_shipper),
    db: Session = Depends(get_db),
):
    """Báo giao xong: chỉ đơn của chính shipper này và đang ở trạng thái Đang giao."""
    order = order_crud.get_order(db, order_id)
    if order is None or order.shipper_id != current_user.id:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy đơn hàng id={order_id}")
    if order.status != "shipping":
        raise HTTPException(
            status_code=400,
            detail="Chỉ báo đã giao được đơn đang ở trạng thái Đang giao (shipping)",
        )

    order = order_crud.update_order_status(db, order, "completed")
    return AdminOrderOut.model_validate(order)
