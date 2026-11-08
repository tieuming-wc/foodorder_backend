"""CRUD cho giỏ hàng: lấy/tạo giỏ của user và thêm món vào giỏ."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.cart import Cart, CartItem


def get_cart(db: Session, user_id: int) -> Cart | None:
    query = select(Cart).where(Cart.user_id == user_id)
    return db.scalar(query)


def get_or_create_cart(db: Session, user_id: int) -> Cart:
    """Mỗi user chỉ có 1 giỏ (UNIQUE carts.user_id). Chưa có thì tạo luôn."""
    cart = get_cart(db, user_id)
    if cart is None:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart


def add_item(db: Session, cart_id: int, food_id: int, quantity: int) -> CartItem:
    """Thêm món vào giỏ. Món đã có thì cộng dồn số lượng, không tạo dòng mới."""
    query = select(CartItem).where(
        CartItem.cart_id == cart_id, CartItem.food_id == food_id
    )
    item = db.scalar(query)

    if item is None:
        item = CartItem(cart_id=cart_id, food_id=food_id, quantity=quantity)
        db.add(item)
    else:
        item.quantity += quantity

    db.commit()
    db.refresh(item)  # lấy lại id, quantity mới do MySQL sinh ra
    return item
