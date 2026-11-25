"""Tạo dữ liệu mẫu cho FE test (chạy 1 lần, chạy lại không bị trùng / không lỗi khoá ngoại).

Cách chạy (đứng trong thư mục backend/):
    python seed.py

Dữ liệu tạo ra:
    - 10 tài khoản / mật khẩu chung 123456, chia 4 vai trò:
        1 admin, 3 khách (khach1..3), 3 nhà hàng (nhahang1..3), 3 shipper (shipper1..3)
    - 5 danh mục (categories)
    - 20 món ăn (items) có link ảnh mạng, chia đủ 5 danh mục
    - Giỏ hàng mẫu cho user1 (2-3 món) để test màn hình giỏ
    - 10 đơn hàng (orders + order_items) rải đủ 5 trạng thái: pending, confirmed,
      shipping, completed, cancelled

Script tự tạo bảng còn thiếu (Base.metadata.create_all) và tự thêm cột mới cho bảng
đã có (app/db/migrations.py) nên chạy được trên database cũ.
Chạy lại script: tài khoản / danh mục / món được cập nhật tại chỗ; đơn hàng và giỏ
của 10 tài khoản seed được tạo lại từ đầu (không nhân đôi dữ liệu).
"""
import sys
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

import app.models  # noqa: F401 - import để SQLAlchemy biết tất cả bảng
from app.core.config import settings
from app.core.security import hash_password
from app.db.migrations import apply_column_migrations
from app.db.session import Base, SessionLocal, engine
from app.models.cart import CartItem
from app.models.category import Category
from app.models.item import Item
from app.models.order import Order, OrderItem
from app.models.user import (
    ROLE_ADMIN,
    ROLE_CUSTOMER,
    ROLE_RESTAURANT,
    ROLE_SHIPPER,
    User,
)

SEED_PASSWORD = "123456"  # mật khẩu chung cho mọi tài khoản mẫu

# ---------------------------------------------------------------------------
# Tài khoản mẫu
# ---------------------------------------------------------------------------
SEED_USERS: list[dict] = [
    # 1 admin
    {
        "username": "admin",
        "full_name": "Quản trị viên",
        "email": "admin@example.com",
        "role": ROLE_ADMIN,
    },
    # 3 khách hàng
    {
        "username": "khach1",
        "full_name": "Nguyễn Văn An",
        "email": "khach1@example.com",
        "role": ROLE_CUSTOMER,
    },
    {
        "username": "khach2",
        "full_name": "Trần Thị Bình",
        "email": "khach2@example.com",
        "role": ROLE_CUSTOMER,
    },
    {
        "username": "khach3",
        "full_name": "Lê Hoàng Cường",
        "email": "khach3@example.com",
        "role": ROLE_CUSTOMER,
    },
    # 3 nhà hàng
    {
        "username": "nhahang1",
        "full_name": "Nhà hàng Cơm Việt",
        "email": "nhahang1@example.com",
        "role": ROLE_RESTAURANT,
    },
    {
        "username": "nhahang2",
        "full_name": "Nhà hàng Phở Hà Nội",
        "email": "nhahang2@example.com",
        "role": ROLE_RESTAURANT,
    },
    {
        "username": "nhahang3",
        "full_name": "Nhà hàng Bún Huế",
        "email": "nhahang3@example.com",
        "role": ROLE_RESTAURANT,
    },
    # 3 shipper
    {
        "username": "shipper1",
        "full_name": "Phạm Minh Tú",
        "email": "shipper1@example.com",
        "role": ROLE_SHIPPER,
    },
    {
        "username": "shipper2",
        "full_name": "Đỗ Văn Hùng",
        "email": "shipper2@example.com",
        "role": ROLE_SHIPPER,
    },
    {
        "username": "shipper3",
        "full_name": "Hoàng Anh Sơn",
        "email": "shipper3@example.com",
        "role": ROLE_SHIPPER,
    },
]

# Tài khoản mẫu của bản cũ (user1..user4). Chỉ xoá khi đúng cả username + email mẫu
# để không làm mất tài khoản thật người dùng đã tạo trùng tên.
LEGACY_SEED_USERS = {
    "user1": "an@example.com",
    "user2": "binh@example.com",
    "user3": "cuong@example.com",
    "user4": "dung@example.com",
}

# ---------------------------------------------------------------------------
# 5 danh mục
# ---------------------------------------------------------------------------
SEED_CATEGORIES: list[dict] = [
    {"name": "Cơm", "description": "Cơm rang, cơm tấm, cơm gà...", "sort_order": 1},
    {"name": "Phở & Bún", "description": "Các món nước: phở, bún, mì", "sort_order": 2},
    {"name": "Đồ uống", "description": "Trà, cà phê, nước ép, sinh tố", "sort_order": 3},
    {"name": "Tráng miệng", "description": "Chè, bánh flan, kem", "sort_order": 4},
    {"name": "Ăn vặt", "description": "Món chiên, bánh mì, nem rán", "sort_order": 5},
]

# ---------------------------------------------------------------------------
# 20 món ăn kèm link ảnh mạng (Unsplash, w=800 cho nhẹ)
# ---------------------------------------------------------------------------
_IMG = "https://images.unsplash.com/photo-{id}?auto=format&fit=crop&w=800&q=80"

SEED_ITEMS: list[dict] = [
    # --- Cơm (4 món) ---
    {
        "name": "Cơm rang dưa bò",
        "description": "Cơm rang tơi với dưa muối và thịt bò mềm, ăn kèm nước tương.",
        "price": Decimal("45000"),
        "category": "Cơm",
        "image_url": _IMG.format(id="1504674900247-0877df9cc836"),
    },
    {
        "name": "Cơm gà xối mỡ",
        "description": "Đùi gà chiên giòn rưới mỡ hành, cơm nóng chan nước dùng.",
        "price": Decimal("55000"),
        "category": "Cơm",
        "image_url": _IMG.format(id="1512058564366-18510be2db19"),
    },
    {
        "name": "Cơm tấm sườn nướng",
        "description": "Sườn nướng mật ong, bì chả, trứng ốp la và nước mắm chua ngọt.",
        "price": Decimal("60000"),
        "category": "Cơm",
        "image_url": _IMG.format(id="1546069901-ba9599a7e63c"),
    },
    {
        "name": "Cơm chiên hải sản",
        "description": "Cơm chiên tôm, mực, trứng và rau củ, thơm mùi tiêu.",
        "price": Decimal("65000"),
        "category": "Cơm",
        "image_url": _IMG.format(id="1512621776951-a57141f2eefd"),
    },
    # --- Phở & Bún (5 món) ---
    {
        "name": "Phở bò tái",
        "description": "Nước dùng xương hầm 8 tiếng, bánh phở mềm, thịt bò tái mỏng.",
        "price": Decimal("50000"),
        "category": "Phở & Bún",
        "image_url": _IMG.format(id="1582878826629-29b7ad1cdc43"),
    },
    {
        "name": "Bún chả Hà Nội",
        "description": "Chả viên và chả miếng nướng than hoa, nước mắm ấm, rau sống.",
        "price": Decimal("45000"),
        "category": "Phở & Bún",
        "image_url": _IMG.format(id="1559847844-5315695dadae"),
    },
    {
        "name": "Bún bò Huế",
        "description": "Nước dùng sả ớt đậm đà, bắp bò, giò heo và chả cua.",
        "price": Decimal("55000"),
        "category": "Phở & Bún",
        "image_url": _IMG.format(id="1569058242253-92a9c755a0ec"),
    },
    {
        "name": "Mì Quảng",
        "description": "Sợi mì vàng, tôm thịt, trứng cút, đậu phộng rang và bánh tráng.",
        "price": Decimal("50000"),
        "category": "Phở & Bún",
        "image_url": _IMG.format(id="1563379926898-05f4575a45d8"),
    },
    {
        "name": "Bún riêu cua",
        "description": "Riêu cua đồng, đậu hũ, cà chua và mắm tôm tuỳ khẩu vị.",
        "price": Decimal("48000"),
        "category": "Phở & Bún",
        "image_url": _IMG.format(id="1547592180-85f173990554"),
    },
    # --- Đồ uống (5 món) ---
    {
        "name": "Trà đá",
        "description": "Trà xanh pha loãng, đá viên mát lạnh.",
        "price": Decimal("5000"),
        "category": "Đồ uống",
        "image_url": _IMG.format(id="1556679343-c7306c1976bc"),
    },
    {
        "name": "Trà sữa trân châu",
        "description": "Trà đen, sữa béo, trân châu đường đen dai mềm.",
        "price": Decimal("30000"),
        "category": "Đồ uống",
        "image_url": _IMG.format(id="1558857563-b371033873b8"),
    },
    {
        "name": "Cà phê sữa đá",
        "description": "Cà phê phin đậm vị Việt Nam, sữa đặc, đá nhiều.",
        "price": Decimal("25000"),
        "category": "Đồ uống",
        "image_url": _IMG.format(id="1509042239860-f550ce710b93"),
    },
    {
        "name": "Nước cam ép",
        "description": "Cam sành vắt tay, không thêm đường, giàu vitamin C.",
        "price": Decimal("30000"),
        "category": "Đồ uống",
        "image_url": _IMG.format(id="1600271886742-f049cd451bba"),
    },
    {
        "name": "Sinh tố bơ",
        "description": "Bơ sáp chín, sữa tươi và sữa đặc, xay đặc mịn.",
        "price": Decimal("35000"),
        "category": "Đồ uống",
        "image_url": _IMG.format(id="1623065422902-30a2d299bbe4"),
    },
    # --- Tráng miệng (3 món) ---
    {
        "name": "Chè ba màu",
        "description": "Đậu xanh, đậu đỏ, thạch lá dứa và nước cốt dừa.",
        "price": Decimal("20000"),
        "category": "Tráng miệng",
        "image_url": _IMG.format(id="1488477181946-6428a0291777"),
    },
    {
        "name": "Bánh flan caramel",
        "description": "Flan trứng mềm mịn, caramel đắng nhẹ, ăn lạnh.",
        "price": Decimal("18000"),
        "category": "Tráng miệng",
        "image_url": _IMG.format(id="1524351199678-941a58a3df50"),
    },
    {
        "name": "Kem dừa",
        "description": "Kem dừa non trong trái dừa, rắc đậu phộng rang.",
        "price": Decimal("25000"),
        "category": "Tráng miệng",
        "image_url": _IMG.format(id="1563805042-7684c019e1cb"),
    },
    # --- Ăn vặt (3 món) ---
    {
        "name": "Nem chua rán",
        "description": "Nem chua bọc bột chiên giòn, chấm tương ớt.",
        "price": Decimal("35000"),
        "category": "Ăn vặt",
        "image_url": _IMG.format(id="1541014741259-de529411b96a"),
    },
    {
        "name": "Bánh mì pate",
        "description": "Bánh mì giòn, pate gan, chả lụa, dưa leo và đồ chua.",
        "price": Decimal("20000"),
        "category": "Ăn vặt",
        "image_url": _IMG.format(id="1509722747041-616f39b57569"),
    },
    {
        "name": "Chả giò chiên",
        "description": "Chả giò nhân thịt, mộc nhĩ, cuốn bánh tráng, chiên vàng.",
        "price": Decimal("40000"),
        "category": "Ăn vặt",
        "image_url": _IMG.format(id="1541529086526-db283c563270"),
    },
]

# ---------------------------------------------------------------------------
# 10 đơn hàng rải đủ 5 trạng thái, mỗi đơn cách nhau vài ngày
# ---------------------------------------------------------------------------
SEED_ORDERS: list[dict] = [
    {
        "username": "khach1",
        "restaurant": "nhahang1",
        "shipper": None,
        "status": "pending",
        "days_ago": 0,
        "note": "Giao tới tầng 3, gọi trước khi tới.",
        "lines": [("Cơm tấm sườn nướng", 1), ("Trà đá", 1)],
    },
    {
        "username": "khach2",
        "restaurant": "nhahang2",
        "shipper": None,
        "status": "pending",
        "days_ago": 1,
        "note": None,
        "lines": [("Phở bò tái", 2)],
    },
    {
        "username": "khach3",
        "restaurant": "nhahang3",
        "shipper": None,
        "status": "pending",
        "days_ago": 2,
        "note": "Ít đá, không bỏ hành.",
        "lines": [("Bún bò Huế", 1), ("Cà phê sữa đá", 1), ("Bánh flan caramel", 2)],
    },
    {
        "username": "khach1",
        "restaurant": "nhahang1",
        "shipper": None,
        "status": "confirmed",
        "days_ago": 4,
        "note": None,
        "lines": [("Cơm gà xối mỡ", 1), ("Nước cam ép", 1)],
    },
    {
        "username": "khach2",
        "restaurant": "nhahang2",
        "shipper": None,
        "status": "confirmed",
        "days_ago": 5,
        "note": "Thêm tương ớt.",
        "lines": [("Bún chả Hà Nội", 2), ("Trà sữa trân châu", 2)],
    },
    {
        "username": "khach3",
        "restaurant": "nhahang3",
        "shipper": "shipper1",
        "status": "shipping",
        "days_ago": 7,
        "note": None,
        "lines": [("Mì Quảng", 1), ("Chả giò chiên", 1)],
    },
    {
        "username": "khach1",
        "restaurant": "nhahang1",
        "shipper": "shipper2",
        "status": "shipping",
        "days_ago": 9,
        "note": "Để trước cửa giúp em.",
        "lines": [("Cơm chiên hải sản", 1), ("Sinh tố bơ", 1)],
    },
    {
        "username": "khach2",
        "restaurant": "nhahang2",
        "shipper": "shipper3",
        "status": "completed",
        "days_ago": 12,
        "note": None,
        "lines": [("Bún riêu cua", 1), ("Chè ba màu", 1), ("Trà đá", 2)],
    },
    {
        "username": "khach3",
        "restaurant": "nhahang3",
        "shipper": "shipper1",
        "status": "completed",
        "days_ago": 15,
        "note": None,
        "lines": [("Cơm rang dưa bò", 2), ("Nem chua rán", 1)],
    },
    {
        "username": "khach1",
        "restaurant": "nhahang1",
        "shipper": None,
        "status": "cancelled",
        "days_ago": 18,
        "note": "Đặt nhầm, xin huỷ.",
        "lines": [("Bánh mì pate", 3), ("Kem dừa", 1)],
    },
]

# Giỏ hàng mẫu cho khach1 để FE có sẵn màn hình giỏ hàng
SEED_CART: list[tuple[str, str, int]] = [
    ("khach1", "Cơm rang dưa bò", 1),
    ("khach1", "Trà sữa trân châu", 2),
    ("khach1", "Chả giò chiên", 1),
]


def _use_utf8_console() -> None:
    """Console Windows mặc định không phải UTF-8 -> print tiếng Việt sẽ lỗi."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            pass


def remove_legacy_seed_users(db: Session) -> list[str]:
    """Xoá 4 tài khoản mẫu cũ (user1..user4) để bộ seed đúng 10 tài khoản.

    Chỉ xoá khi username VÀ email đều khớp dữ liệu mẫu cũ -> không đụng tài khoản thật.
    Xoá user sẽ cascade xoá đơn / giỏ của chính tài khoản mẫu đó.
    """
    removed: list[str] = []
    for username, email in LEGACY_SEED_USERS.items():
        user = db.scalar(select(User).where(User.username == username))
        if user is not None and user.email == email:
            db.delete(user)
            removed.append(username)
    if removed:
        db.commit()
    return removed


def seed_users(db: Session) -> dict[str, User]:
    """Tạo (hoặc cập nhật) 10 tài khoản theo vai trò. Trả về map username -> User."""
    users: dict[str, User] = {}
    for data in SEED_USERS:
        role = data["role"]
        is_admin = role == ROLE_ADMIN
        user = db.scalar(select(User).where(User.username == data["username"]))
        if user is None:
            user = User(
                username=data["username"],
                hashed_password=hash_password(SEED_PASSWORD),
                full_name=data["full_name"],
                email=data["email"],
                is_active=True,
                is_admin=is_admin,
                role=role,
            )
            db.add(user)
        else:
            # Chạy lại script: cập nhật thông tin + đảm bảo đăng nhập được
            user.full_name = data["full_name"]
            user.email = data["email"]
            user.is_active = True
            user.is_admin = is_admin
            user.role = role
            user.hashed_password = hash_password(SEED_PASSWORD)
        users[data["username"]] = user
    db.commit()
    for user in users.values():
        db.refresh(user)
    return users


def seed_categories(db: Session) -> dict[str, Category]:
    categories: dict[str, Category] = {}
    for data in SEED_CATEGORIES:
        category = db.scalar(select(Category).where(Category.name == data["name"]))
        if category is None:
            category = Category(**data)
            db.add(category)
        else:
            category.description = data["description"]
            category.sort_order = data["sort_order"]
        categories[data["name"]] = category
    db.commit()
    for category in categories.values():
        db.refresh(category)
    return categories


def seed_items(db: Session, categories: dict[str, Category]) -> dict[str, Item]:
    """20 món ăn. category_id phải trỏ tới danh mục vừa tạo (tránh lỗi khoá ngoại)."""
    items: dict[str, Item] = {}
    for data in SEED_ITEMS:
        category = categories[data["category"]]
        item = db.scalar(select(Item).where(Item.name == data["name"]))
        if item is None:
            item = Item(
                name=data["name"],
                description=data["description"],
                price=data["price"],
                image_url=data["image_url"],
                category_id=category.id,
            )
            db.add(item)
        else:
            item.description = data["description"]
            item.price = data["price"]
            item.image_url = data["image_url"]
            item.category_id = category.id
        items[data["name"]] = item
    db.commit()
    for item in items.values():
        db.refresh(item)
    return items


def reset_seed_orders(db: Session, users: dict[str, User]) -> None:
    """Xoá đơn cũ của 5 tài khoản seed (kèm order_items) để chạy lại không bị nhân đôi."""
    user_ids = [user.id for user in users.values()]
    orders = db.scalars(select(Order).where(Order.user_id.in_(user_ids))).all()
    for order in orders:
        db.delete(order)  # cascade="all, delete-orphan" xoá luôn order_items
    db.commit()


def seed_orders(
    db: Session, users: dict[str, User], items: dict[str, Item]
) -> None:
    now = datetime.now()
    for data in SEED_ORDERS:
        user = users[data["username"]]
        restaurant = users[data["restaurant"]]
        shipper = users[data["shipper"]] if data.get("shipper") else None
        created_at = now - timedelta(days=data["days_ago"], hours=2)

        order = Order(
            user_id=user.id,  # FK phải là id thật của user vừa tạo
            restaurant_id=restaurant.id,
            shipper_id=shipper.id if shipper else None,
            status=data["status"],
            note=data["note"],
            total_amount=Decimal("0"),
            created_at=created_at,
            updated_at=created_at,
            canceled_at=created_at if data["status"] == "cancelled" else None,
        )

        total = Decimal("0")
        for item_name, quantity in data["lines"]:
            item = items[item_name]
            total += item.price * quantity
            order.items.append(
                OrderItem(
                    item_id=item.id,
                    item_name=item.name,
                    unit_price=item.price,
                    quantity=quantity,
                )
            )
        order.total_amount = total
        db.add(order)
    db.commit()


def seed_cart(
    db: Session, users: dict[str, User], items: dict[str, Item]
) -> None:
    """Giỏ hàng mẫu (tạo lại từ đầu mỗi lần chạy)."""
    user_ids = [user.id for user in users.values()]
    for cart_item in db.scalars(select(CartItem).where(CartItem.user_id.in_(user_ids))).all():
        db.delete(cart_item)
    db.commit()

    for username, item_name, quantity in SEED_CART:
        db.add(
            CartItem(
                user_id=users[username].id,
                item_id=items[item_name].id,
                quantity=quantity,
            )
        )
    db.commit()


def print_summary(db: Session) -> None:
    print("\n===== DỮ LIỆU MẪU ĐÃ SẴN SÀNG =====")
    print(f"Users      : {len(SEED_USERS)} tài khoản / mật khẩu chung {SEED_PASSWORD}")
    print(f"Categories : {db.query(Category).count()}")
    print(f"Items      : {db.query(Item).count()}")
    print(f"Cart items : {db.query(CartItem).count()}")
    print(f"Orders     : {db.query(Order).count()}")
    print(f"Order lines: {db.query(OrderItem).count()}")
    print("\nTài khoản đăng nhập thử (mật khẩu chung 123456):")
    groups = {
        "admin": "admin",
        "khách hàng": "khach1, khach2, khach3",
        "nhà hàng": "nhahang1, nhahang2, nhahang3",
        "shipper": "shipper1, shipper2, shipper3",
    }
    for label, accounts in groups.items():
        print(f"  {label:<11}: {accounts}")
    print("\nTrang quản trị:")
    print("  /login       đăng nhập, tự chuyển theo vai trò")
    print("  /admin       quản trị đơn hàng + tài khoản")
    print("  /restaurant  nhà hàng xác nhận đơn")
    print("  /shipper     shipper nhận giao + báo đã giao")
    print("\nĐơn hàng theo trạng thái:")
    for status in ("pending", "confirmed", "shipping", "completed", "cancelled"):
        count = db.query(Order).filter(Order.status == status).count()
        print(f"  {status:<10}: {count}")
    print("\nGợi ý test luồng đặt hàng: đăng nhập khach1 -> GET /api/cart (có sẵn 3 món)")
    print("-> POST /api/orders/checkout -> nhahang1 xác nhận -> shipper1 nhận giao -> đã giao.")


def main() -> int:
    _use_utf8_console()
    print(f"Kết nối MySQL {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME} ...")
    try:
        # Tạo bảng còn thiếu + thêm cột mới cho bảng đã tồn tại (chạy nhiều lần không lỗi)
        Base.metadata.create_all(bind=engine)
        added = apply_column_migrations(engine)
        if added:
            print(f"Đã thêm cột còn thiếu: {', '.join(added)}")
    except SQLAlchemyError as error:
        print("\n[LỖI] Không kết nối / không tạo được bảng trong MySQL.")
        print("  - Kiểm tra MySQL đã bật chưa, và DB_HOST/DB_PORT/DB_USER/DB_PASSWORD/DB_NAME trong .env")
        print("  - Nếu chưa có database: chạy sql/init.sql bằng MySQL Workbench")
        print(f"  Chi tiết: {error}")
        return 1

    db = SessionLocal()
    try:
        removed = remove_legacy_seed_users(db)
        if removed:
            print(f"Đã xoá tài khoản mẫu cũ: {', '.join(removed)}")
        users = seed_users(db)
        categories = seed_categories(db)
        items = seed_items(db, categories)
        reset_seed_orders(db, users)
        seed_orders(db, users, items)
        seed_cart(db, users, items)
        print_summary(db)
    except SQLAlchemyError as error:
        db.rollback()
        print(f"\n[LỖI] Ghi dữ liệu mẫu thất bại: {error}")
        return 1
    finally:
        db.close()

    print("\nXong! Chạy server: uvicorn app.main:app --reload")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
