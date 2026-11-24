from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.item import Item
from app.models.order import Order, OrderItem
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.order import OrderCreate, OrderOut

router = APIRouter(prefix="/orders", tags=["Orders"])


def discount_for(coupon: str | None, subtotal: Decimal) -> tuple[Decimal, str | None]:
    code = (coupon or "").strip().upper()
    if code == "WELCOME15":
        if subtotal < Decimal("300000"):
            return Decimal("0"), code
        return min(subtotal * Decimal("0.15"), Decimal("300000")), code
    if code == "SAVORIS10":
        return min(subtotal * Decimal("0.10"), Decimal("200000")), code
    if code:
        raise HTTPException(status_code=400, detail="Mã giảm giá không hợp lệ.")
    return Decimal("0"), None


@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(
    data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    subtotal = Decimal("0")
    order_items: list[tuple[Item, int]] = []

    for entry in data.items:
        item = db.get(Item, entry.item_id)
        if item is None or not item.is_available:
            raise HTTPException(
                status_code=404,
                detail=f"Món ăn ID {entry.item_id} không tồn tại.",
            )
        subtotal += Decimal(str(item.price)) * entry.quantity
        order_items.append((item, entry.quantity))

    discount, coupon = discount_for(data.coupon_code, subtotal)
    if data.coupon_code and data.coupon_code.strip().upper() == "WELCOME15" and subtotal < Decimal("300000"):
        raise HTTPException(status_code=400, detail="Mã WELCOME15 chỉ áp dụng cho đơn từ 300.000đ.")

    shipping = Decimal("30000") if subtotal > 0 else Decimal("0")
    total = max(Decimal("0"), subtotal + shipping - discount)
    order = Order(
        user_id=current_user.id,
        recipient_name=data.recipient_name.strip(),
        phone_number=data.phone_number,
        address_line=data.address_line.strip(),
        note=data.note.strip() if data.note else None,
        subtotal=subtotal,
        shipping_fee=shipping,
        discount_amount=discount,
        coupon_code=coupon,
        total_amount=total,
        payment_method=data.payment_method,
        payment_status="pending",
        status="pending",
    )
    db.add(order)
    db.flush()

    for item, quantity in order_items:
        unit_price = Decimal(str(item.price))
        db.add(OrderItem(
            order_id=order.id,
            item_id=item.id,
            item_name=item.name,
            quantity=quantity,
            unit_price=unit_price,
            total_price=unit_price * quantity,
        ))

    db.commit()
    db.refresh(order)
    return order


@router.get("", response_model=list[OrderOut])
def list_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    orders = db.scalars(
        select(Order).where(Order.user_id == current_user.id).order_by(Order.created_at.desc())
    )
    return list(orders)


@router.get("/{order_id}", response_model=OrderOut)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = db.scalar(
        select(Order).where(Order.id == order_id, Order.user_id == current_user.id)
    )
    if order is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng.")
    return order
