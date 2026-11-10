"""CRUD cho giỏ hàng: lấy/tạo giỏ của user, thêm/sửa/xoá món trong giỏ.

Mọi hàm đều nhận `cart_id` của **chính user đang đăng nhập**, nên không có cách nào
chạm vào dòng của giỏ khác.
"""
from sqlalchemy import delete, select
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


def get_item(db: Session, cart_id: int, food_id: int) -> CartItem | None:
    query = select(CartItem).where(
        CartItem.cart_id == cart_id, CartItem.food_id == food_id
    )
    return db.scalar(query)


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


def update_quantity(
    db: Session, cart_id: int, food_id: int, quantity: int
) -> CartItem | None:
    """Đặt lại số lượng của 1 dòng trong giỏ. Món không có trong giỏ -> None."""
    item = get_item(db, cart_id, food_id)
    if item is None:
        return None

    item.quantity = quantity
    db.commit()
    db.refresh(item)
    return item


def delete_item(db: Session, cart_id: int, food_id: int) -> bool:
    """Xoá 1 món khỏi giỏ. Món không có trong giỏ -> False."""
    item = get_item(db, cart_id, food_id)
    if item is None:
        return False

    db.delete(item)
    db.commit()
    return True


def clear_cart(db: Session, cart_id: int) -> int:
    """Xoá toàn bộ dòng của 1 giỏ (giữ lại bản ghi `carts`). Trả về số dòng đã xoá."""
    result = db.execute(delete(CartItem).where(CartItem.cart_id == cart_id))
    db.commit()
    return result.rowcount
