from math import ceil
from typing import Optional
from fastapi import APIRouter, Depends, Query
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
    db: Session = Depends(get_db)
):
    query = db.query(Food).filter(Food.is_available == True)

    if keyword:
        search_keyword = f"%{keyword.strip()}%"
        query = query.filter(Food.name.ilike(search_keyword))

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
