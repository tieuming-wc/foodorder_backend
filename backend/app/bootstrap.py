from sqlalchemy import inspect, select, text
from sqlalchemy.orm import Session

from app.db.session import Base, engine
from app.models.item import Item

MENU_ITEMS = [
    {
        "name": "Bít tết bò Wagyu",
        "description": "Thăn Wagyu, rau củ theo mùa và sốt tiêu đen.",
        "price": 1250000,
        "category": "Món chính",
        "image_url": "https://images.unsplash.com/photo-1546039907-7fa05f864c02?auto=format&fit=crop&w=900&q=85",
        "delivery_time": "25–35 phút",
        "rating": 4.9,
    },
    {
        "name": "Cá hồi áp chảo",
        "description": "Cá hồi tươi, khoai nghiền và sốt chanh bơ.",
        "price": 395000,
        "category": "Hải sản",
        "image_url": "https://images.unsplash.com/photo-1467003909585-2f8a72700288?auto=format&fit=crop&w=900&q=85",
        "delivery_time": "20–30 phút",
        "rating": 4.8,
    },
    {
        "name": "Mỳ Ý nấm Truffle",
        "description": "Mỳ Ý, nấm tươi và sốt kem truffle thơm béo.",
        "price": 285000,
        "category": "Mì & Pasta",
        "image_url": "https://images.unsplash.com/photo-1473093295043-cdd812d0e601?auto=format&fit=crop&w=900&q=85",
        "delivery_time": "20–25 phút",
        "rating": 4.9,
    },
    {
        "name": "Tiramisu cổ điển",
        "description": "Mascarpone, cà phê espresso và cacao.",
        "price": 125000,
        "category": "Tráng miệng",
        "image_url": "https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?auto=format&fit=crop&w=900&q=85",
        "delivery_time": "15–20 phút",
        "rating": 4.8,
    },
    {
        "name": "Cơm gà sa tế",
        "description": "Cơm gà ướp sa tế, rau củ và nước sốt đặc trưng.",
        "price": 95000,
        "category": "Món chính",
        "image_url": "https://images.unsplash.com/photo-1603133872878-684f208fb84b?auto=format&fit=crop&w=900&q=85",
        "delivery_time": "20–30 phút",
        "rating": 4.7,
    },
    {
        "name": "Pizza Burrata",
        "description": "Pizza nướng lò, burrata, cà chua và húng quế.",
        "price": 320000,
        "category": "Món chính",
        "image_url": "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?auto=format&fit=crop&w=900&q=85",
        "delivery_time": "25–35 phút",
        "rating": 4.8,
    },
    {
        "name": "Salad bơ chanh",
        "description": "Bơ, rau xanh, cà chua bi và sốt chanh dây.",
        "price": 145000,
        "category": "Món chính",
        "image_url": "https://images.unsplash.com/photo-1546793665-c74683f339c1?auto=format&fit=crop&w=900&q=85",
        "delivery_time": "15–20 phút",
        "rating": 4.6,
    },
    {
        "name": "Mỳ Ý hải sản",
        "description": "Mỳ Ý, tôm, mực và nước sốt cà chua hải sản.",
        "price": 265000,
        "category": "Mì & Pasta",
        "image_url": "https://images.unsplash.com/photo-1563379926898-05f4575a45d8?auto=format&fit=crop&w=900&q=85",
        "delivery_time": "20–30 phút",
        "rating": 4.8,
    },
    {
        "name": "Tôm nướng bơ tỏi",
        "description": "Tôm biển nướng bơ tỏi, salad và bánh mì bơ.",
        "price": 345000,
        "category": "Hải sản",
        "image_url": "https://images.unsplash.com/photo-1625944525533-473f1a3d54e7?auto=format&fit=crop&w=900&q=85",
        "delivery_time": "25–30 phút",
        "rating": 4.9,
    },
    {
        "name": "Súp bí đỏ",
        "description": "Súp bí đỏ xay mịn, kem tươi và hạt bí rang.",
        "price": 95000,
        "category": "Món chính",
        "image_url": "https://images.unsplash.com/photo-1476718406336-bb5a9690ee2a?auto=format&fit=crop&w=900&q=85",
        "delivery_time": "15–20 phút",
        "rating": 4.5,
    },
    {
        "name": "Bánh mousse xoài",
        "description": "Mousse xoài tươi, kem phô mai và vụn bánh.",
        "price": 115000,
        "category": "Tráng miệng",
        "image_url": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=900&q=85",
        "delivery_time": "15–20 phút",
        "rating": 4.7,
    },
    {
        "name": "Trà đào cam sả",
        "description": "Trà đào, cam tươi, sả và đá mát lạnh.",
        "price": 65000,
        "category": "Đồ uống",
        "image_url": "https://images.unsplash.com/photo-1556679343-c7306c1976bc?auto=format&fit=crop&w=900&q=85",
        "delivery_time": "10–15 phút",
        "rating": 4.7,
    },
]


def migrate_items_table() -> None:
    inspector = inspect(engine)
    if not inspector.has_table("items"):
        return

    existing_columns = {column["name"] for column in inspector.get_columns("items")}
    migrations = {
        "category": "VARCHAR(100) NOT NULL DEFAULT 'Món chính'",
        "image_url": "VARCHAR(500) NULL",
        "delivery_time": "VARCHAR(50) NOT NULL DEFAULT '25–35 phút'",
        "rating": "DECIMAL(3, 1) NOT NULL DEFAULT 0",
        "is_available": "BOOLEAN NOT NULL DEFAULT TRUE",
    }

    with engine.begin() as connection:
        for column_name, column_definition in migrations.items():
            if column_name not in existing_columns:
                connection.execute(
                    text(f"ALTER TABLE items ADD COLUMN {column_name} {column_definition}")
                )


def initialize_database() -> None:
    migrate_items_table()
    Base.metadata.create_all(bind=engine)

    with Session(engine) as db:
        existing_names = set(db.scalars(select(Item.name)).all())
        missing_items = [
            Item(**item)
            for item in MENU_ITEMS
            if item["name"] not in existing_names
        ]
        if missing_items:
            db.add_all(missing_items)
            db.commit()
