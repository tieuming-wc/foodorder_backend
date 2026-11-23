from pydantic import BaseModel, Field


class TopFoodItem(BaseModel):
    food_id: int
    name: str
    total_sold: int = Field(ge=0)
    total_revenue: float = Field(ge=0)


class DashboardOut(BaseModel):
    total_revenue: float = Field(ge=0)
    total_orders: int = Field(ge=0)
    total_users: int = Field(ge=0)
    top_foods: list[TopFoodItem] = Field(default_factory=list)
