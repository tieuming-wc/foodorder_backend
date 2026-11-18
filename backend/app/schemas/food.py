from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List
from app.schemas.category import CategoryResponse


class FoodBase(BaseModel):
    name: str
    description: str | None = None
    price: Decimal = Field(..., gt=0,
                           description="Giá món ăn bắt buộc phải lớn hơn 0")
    image: str | None = None
    is_available: bool = True


class FoodCreate(FoodBase):
    category_id: int = Field(..., description="ID danh mục hợp lệ")


class FoodUpdate(BaseModel):
    category_id: int | None = None
    name: str | None = None
    description: str | None = None
    price: Decimal | None = Field(
        None, gt=0, description="Nếu cập nhật giá, giá phải lớn hơn 0")
    image: str | None = None
    is_available: bool | None = None


class FoodResponse(FoodBase):
    id: int
    category_id: int
    sales_count: int
    created_at: datetime
    category: CategoryResponse | None = None

    class Config:
        from_attributes = True


class FoodPaginatedResponse(BaseModel):
    items: List[FoodResponse]
    total: int
    page: int
    size: int
    total_pages: int

    class Config:
        from_attributes = True
