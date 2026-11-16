"""Import các model ở đây để SQLAlchemy đăng ký bảng vào Base.metadata.

Thêm model mới (vd models/product.py) thì thêm 1 dòng import bên dưới, nếu không
bảng sẽ không được tạo tự động khi server khởi động.
"""
from app.models.item import Item  # noqa: F401
from app.models.order import Order, OrderItem  # noqa: F401
from app.models.user import User  # noqa: F401

__all__ = ["Item", "Order", "OrderItem", "User"]
