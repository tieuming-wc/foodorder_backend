"""API giỏ hàng. Đường dẫn đầy đủ: /api/cart

    GET  /api/cart         giỏ của tôi (từng dòng + thành tiền + tổng tiền)
    POST /api/cart/items   thêm món (món đã có -> cộng dồn số lượng)

Cả 2 API đều bắt buộc đăng nhập -> dùng Depends(get_current_user).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.crud import cart as cart_crud
from app.db.session import get_db
from app.models.food import Food
from app.models.user import User
from app.schemas.cart import CartItemCreate, CartItemOut, CartOut

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
