"""CRUD = các hàm đọc/ghi DB cho bảng items. Router gọi vào đây, không viết SQL trong router."""
from sqlalchemy import asc, desc, select
from sqlalchemy.orm import Session

from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate

# Các kiểu sắp xếp cho GET /api/items. Sắp theo giá thì thêm id để hai món cùng giá
# luôn ra cùng một thứ tự (nếu không, MySQL có thể đổi chỗ chúng giữa các lần gọi).
SORT_ORDERS = {
    "id_desc": (desc(Item.id),),
    "id_asc": (asc(Item.id),),
    "price_asc": (asc(Item.price), asc(Item.id)),
    "price_desc": (desc(Item.price), asc(Item.id)),
}


def get_items(
    db: Session, keyword: str | None = None, sort: str = "id_desc"
) -> list[Item]:
    query = select(Item).order_by(*SORT_ORDERS[sort])
    if keyword:
        query = query.where(Item.name.contains(keyword))
    return list(db.scalars(query))


def get_item(db: Session, item_id: int) -> Item | None:
    return db.get(Item, item_id)


def create_item(db: Session, data: ItemCreate) -> Item:
    item = Item(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)  # lấy lại id, created_at... do MySQL sinh ra
    return item


def update_item(db: Session, item: Item, data: ItemUpdate) -> Item:
    # exclude_unset: chỉ lấy các trường FE thực sự gửi lên
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


def delete_item(db: Session, item: Item) -> None:
    db.delete(item)
    db.commit()
