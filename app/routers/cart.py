"""API giỏ hàng của user đang đăng nhập. Đường dẫn đầy đủ:

    GET    /api/cart              xem giỏ (kèm tổng số lượng + tổng tiền)
    POST   /api/cart              thêm món  {"item_id": 1, "quantity": 2}
    PUT    /api/cart/{item_id}    đổi số lượng  {"quantity": 3}
    DELETE /api/cart/{item_id}    bỏ 1 món khỏi giỏ
    DELETE /api/cart              xoá sạch giỏ

Giỏ luôn lấy theo user trong token: không ai đọc/sửa được giỏ của người khác.
Đặt hàng (POST /api/orders/checkout) sẽ tự xoá các món vừa đặt khỏi giỏ.
"""
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.crud import cart as cart_crud
from app.crud import item as item_crud
from app.db.session import get_db
from app.models.user import User
from app.schemas.cart import CartItemAdd, CartItemOut, CartItemUpdate, CartOut

router = APIRouter(prefix="/cart", tags=["Cart"])


def _build_cart(db: Session, user_id: int) -> CartOut:
    cart_items = cart_crud.get_cart_items(db, user_id)
    items = [CartItemOut.model_validate(cart_item) for cart_item in cart_items]
    return CartOut(
        items=items,
        total_quantity=sum(cart_item.quantity for cart_item in cart_items),
        total_amount=sum(float(cart_item.subtotal) for cart_item in cart_items),
    )


@router.get("", response_model=CartOut)
def get_my_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _build_cart(db, current_user.id)


@router.post("", response_model=CartOut, status_code=status.HTTP_201_CREATED)
def add_to_my_cart(
    data: CartItemAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Thêm món. Món đã có trong giỏ thì cộng dồn số lượng."""
    if item_crud.get_item(db, data.item_id) is None:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy món id={data.item_id}")
    cart_crud.add_to_cart(db, current_user.id, data.item_id, data.quantity)
    return _build_cart(db, current_user.id)


@router.put("/{item_id}", response_model=CartOut)
def update_my_cart_item(
    item_id: int,
    data: CartItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cart_item = cart_crud.get_cart_item(db, current_user.id, item_id)
    if cart_item is None:
        raise HTTPException(status_code=404, detail=f"Món id={item_id} không có trong giỏ")
    cart_crud.update_quantity(db, cart_item, data.quantity)
    return _build_cart(db, current_user.id)


@router.delete("/{item_id}", response_model=CartOut)
def remove_my_cart_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cart_item = cart_crud.get_cart_item(db, current_user.id, item_id)
    if cart_item is None:
        raise HTTPException(status_code=404, detail=f"Món id={item_id} không có trong giỏ")
    cart_crud.remove_cart_item(db, cart_item)
    return _build_cart(db, current_user.id)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def clear_my_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    cart_crud.clear_cart(db, current_user.id)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
