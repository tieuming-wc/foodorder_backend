from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class RecommendedFoodItem(BaseModel):
    id: int
    category_id: int
    name: str
    price: Decimal
    image: str | None = None
    sales_count: int = 0
    reason: str | None = None

    model_config = ConfigDict(from_attributes=True)
