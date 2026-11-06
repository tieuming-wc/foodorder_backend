from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel
from app.schemas.category import CategoryResponse


class FoodBase(BaseModel):
    name: str
    description: str | None = None
    price: Decimal
    image: str | None = None
    is_available: bool = True
    display_order: int = 0


class FoodCreate(FoodBase):
    category_id: int


class FoodUpdate(BaseModel):
    category_id: int | None = None
    name: str | None = None
    description: str | None = None
    price: Decimal | None = None
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
