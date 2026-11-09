# Import mọi model ở đây để Base.metadata.create_all() "nhìn thấy" và tạo bảng.
# Thêm model mới -> nhớ thêm 1 dòng import vào file này.
from app.models.cart import Cart, CartItem  # noqa: F401
from app.models.food import Food  # noqa: F401
from app.models.item import Item  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.category import Category  # noqa: F401
