"""CRUD = các hàm đọc/ghi DB cho bảng categories."""
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.item import Item
from app.schemas.category import CategoryCreate, CategoryUpdate


def get_categories(db: Session) -> list[tuple[Category, int]]:
    """Danh sách danh mục (sort_order tăng dần, rồi theo tên) kèm số món mỗi danh mục."""
    rows = db.execute(
        select(Category, func.count(Item.id))
        .outerjoin(Item, Item.category_id == Category.id)
        .group_by(Category.id)
        .order_by(Category.sort_order, Category.name)
    ).all()
    return [(category, count) for category, count in rows]


def get_category(db: Session, category_id: int) -> Category | None:
    return db.get(Category, category_id)


def get_category_by_name(db: Session, name: str) -> Category | None:
    return db.scalar(select(Category).where(Category.name == name))


def create_category(db: Session, data: CategoryCreate) -> Category:
    category = Category(**data.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update_category(db: Session, category: Category, data: CategoryUpdate) -> Category:
    # exclude_unset: chỉ lấy các trường FE thực sự gửi lên
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(category, field, value)
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category: Category) -> None:
    """Xoá danh mục. Các món thuộc danh mục này chỉ bị mất category_id (SET NULL)."""
    db.delete(category)
    db.commit()
