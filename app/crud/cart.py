"""CRUD = các hàm đọc/ghi DB cho bảng cart_items (giỏ hàng của 1 user)."""
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.cart import CartItem

# Số lượng tối đa của 1 món trong giỏ (khớp schema quantity le=99)
MAX_QUANTITY = 99


def get_cart_items(db: Session, user_id: int) -> list[CartItem]:
    """Toàn bộ món trong giỏ của user, món thêm gần nhất lên đầu."""
    return list(
        db.scalars(
            select(CartItem)
            .where(CartItem.user_id == user_id)
            .order_by(CartItem.created_at.desc(), CartItem.id.desc())
        )
    )


def get_cart_item(db: Session, user_id: int, item_id: int) -> CartItem | None:
    """1 dòng giỏ theo món. Lọc theo user_id -> không đọc được giỏ của người khác."""
    return db.scalar(
        select(CartItem).where(
            CartItem.user_id == user_id, CartItem.item_id == item_id
        )
    )


def add_to_cart(db: Session, user_id: int, item_id: int, quantity: int) -> CartItem:
    """Thêm món vào giỏ. Món đã có thì cộng dồn (không vượt MAX_QUANTITY)."""
    cart_item = get_cart_item(db, user_id, item_id)
    if cart_item is None:
        cart_item = CartItem(user_id=user_id, item_id=item_id, quantity=quantity)
        db.add(cart_item)
    else:
        cart_item.quantity = min(cart_item.quantity + quantity, MAX_QUANTITY)
    db.commit()
    db.refresh(cart_item)
    return cart_item


def update_quantity(db: Session, cart_item: CartItem, quantity: int) -> CartItem:
    cart_item.quantity = min(quantity, MAX_QUANTITY)
    db.commit()
    db.refresh(cart_item)
    return cart_item


def remove_cart_item(db: Session, cart_item: CartItem) -> None:
    db.delete(cart_item)
    db.commit()


def clear_cart(db: Session, user_id: int) -> int:
    """Xoá sạch giỏ của user, trả về số dòng đã xoá.

    Gọi hàm này SAU KHI tạo đơn nhưng trong cùng transaction (không commit sớm) để
    đơn và giỏ luôn đi đôi với nhau: đơn lỗi thì giỏ còn nguyên.
    """
    result = db.execute(delete(CartItem).where(CartItem.user_id == user_id))
    return result.rowcount or 0
