from math import ceil
from typing import Optional
from decimal import Decimal
from fastapi import HTTPException, status, APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.food import Food
from pydantic import BaseModel
from typing import List
from app.schemas.food import FoodResponse, FoodPaginatedResponse

router = APIRouter(
    prefix="/foods",
    tags=["Foods"]
)


@router.get("", response_model=FoodPaginatedResponse)
def get_foods(
    page: int = Query(1, ge=1, description="Số trang hiện tại"),
    size: int = Query(12, ge=1, le=100,
                      description="Số lượng món trên 1 trang"),
    keyword: Optional[str] = Query(
        None, description="Từ khóa tìm kiếm theo tên món"),
        category_id: Optional[int] = Query(
            None, description="Lọc theo ID danh mục"),
    min_price: Optional[Decimal] = Query(
        None, ge=0, description="Giá tối thiểu"),
    max_price: Optional[Decimal] = Query(None, ge=0, description="Giá tối đa"),
    sort_by: Optional[str] = Query(
        None,
        description="Sắp xếp giá tăng, giá giảm, món mới nhất, món bán chạy"
    ),
    db: Session = Depends(get_db)
):
    query = db.query(Food).filter(Food.is_available == True)

    if keyword:
        search_keyword = f"%{keyword.strip()}%"
        query = query.filter(Food.name.ilike(search_keyword))

    if category_id is not None:
        query = query.filter(Food.category_id == category_id)

    if min_price is not None:
        query = query.filter(Food.price >= min_price)
    if max_price is not None:
        query = query.filter(Food.price <= max_price)

    if sort_by == "price_asc":
        query = query.order_by(Food.price.asc())
    elif sort_by == "price_desc":
        query = query.order_by(Food.price.desc())
    elif sort_by == "latest":
        query = query.order_by(Food.created_at.desc())
    elif sort_by == "best_seller":
        query = query.order_by(Food.sales_count.desc())
    else:
        query = query.order_by(Food.id.asc())

    total = query.count()

    total_pages = ceil(total / size) if total > 0 else 0

    offset = (page - 1) * size
    foods = query.offset(offset).limit(size).all()

    return {
        "items": foods,
        "total": total,
        "page": page,
        "size": size,
        "total_pages": total_pages
    }


@router.get("/{food_id}", response_model=FoodResponse)
def get_food_detail(food_id: int, db: Session = Depends(get_db)):
    food = db.query(Food).filter(Food.id == food_id).first()

    if not food or not food.is_available:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Món ăn không tồn tại hoặc đã ngừng bán."
        )

    return food
