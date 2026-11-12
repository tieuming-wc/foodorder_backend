"""API giỏ hàng. Đường dẫn đầy đủ: /api/cart

    GET    /api/cart              giỏ của tôi (từng dòng + thành tiền + tổng tiền)
    POST   /api/cart/items        thêm món (món đã có -> cộng dồn số lượng)
    PUT    /api/cart/items/{id}   đặt lại số lượng 1 món (1..99)
    DELETE /api/cart/items/{id}   xoá 1 món khỏi giỏ
    DELETE /api/cart              xoá sạch giỏ

{id} là food_id (id của món), giống food_id mà POST /cart/items và GET /api/cart dùng.

Mọi API đều bắt buộc đăng nhập -> dùng Depends(get_current_user) và luôn làm việc
trên giỏ của chính user đó: món không có trong giỏ của mình -> 404.

Tiền không bao giờ lấy từ client: thành tiền/tổng tiền do schema tính lại từ giá
hiện tại trong bảng `foods` (xem app/schemas/cart.py).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.crud import cart as cart_crud
from app.db.session import get_db
from app.models.food import Food
from app.models.user import User
from app.schemas.cart import CartItemCreate, CartItemOut, CartItemUpdate, CartOut

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.get("", response_model=CartOut)
def get_my_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Giỏ hàng hiện tại của user đang đăng nhập (chưa có thì trả giỏ rỗng)."""
    return cart_crud.get_or_create_cart(db, current_user.id)


@router.post("/items", response_model=CartItemOut)
def add_cart_item(
    data: CartItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Thêm món vào giỏ. Món đã có thì cộng dồn số lượng vào dòng cũ."""
    food = db.get(Food, data.food_id)
    if food is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy món ăn id={data.food_id}",
        )
    if not food.is_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Món '{food.name}' đã ngừng bán",
        )

    cart = cart_crud.get_or_create_cart(db, current_user.id)
    return cart_crud.add_item(db, cart.id, food.id, data.quantity)


@router.put("/items/{food_id}", response_model=CartItemOut)
def update_cart_item(
    food_id: int,
    data: CartItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Đặt lại số lượng của 1 món đã có trong giỏ của tôi (1..99).

    Món không có trong giỏ của mình (kể cả của user khác) -> 404.
    """
    cart = cart_crud.get_cart(db, current_user.id)
    item = None
    if cart is not None:
        item = cart_crud.update_quantity(db, cart.id, food_id, data.quantity)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Món id={food_id} không có trong giỏ hàng của bạn",
        )
    return item


@router.delete("/items/{food_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cart_item(
    food_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Xoá 1 món khỏi giỏ của tôi. Món không có trong giỏ của mình -> 404."""
    cart = cart_crud.get_cart(db, current_user.id)
    if cart is None or not cart_crud.delete_item(db, cart.id, food_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Món id={food_id} không có trong giỏ hàng của bạn",
        )


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def clear_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Xoá sạch giỏ của tôi. Giỏ đang trống (hoặc chưa có giỏ) vẫn trả 204."""
    cart = cart_crud.get_cart(db, current_user.id)
    if cart is not None:
        cart_crud.clear_cart(db, cart.id)
