"""Schema trả về giỏ hàng: kèm thông tin món, số lượng và thành tiền.

- `line_total`  = đơn giá của món × số lượng (thành tiền từng dòng).
- `total_price` = tổng thành tiền của cả giỏ.
- `total_quantity` = tổng số lượng món trong giỏ.

Các trường tính toán dùng `@computed_field` nên FE nhận được ngay trong JSON,
không phải tự nhân/cộng lại ở phía client.
"""
from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator


def _to_money(value: Decimal | float | int) -> float:
    """Làm tròn 2 chữ số thập phân và trả về float cho FE dễ dùng."""
    return float(Decimal(str(value)).quantize(Decimal("0.01")))


class FoodBrief(BaseModel):
    """Thông tin món cần hiển thị trong giỏ (không lôi cả mô tả/tồn kho)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price: float
    image_url: str | None = None
    is_available: bool


class CartItemOut(BaseModel):
    """Một dòng trong giỏ: món nào, bao nhiêu, thành tiền bao nhiêu."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    food_id: int
    quantity: int = Field(ge=1, examples=[2])
    food: FoodBrief

    @computed_field  # type: ignore[prop-decorator]
    @property
    def line_total(self) -> float:
        """Thành tiền của dòng = đơn giá × số lượng."""
        return _to_money(Decimal(str(self.food.price)) * self.quantity)


class CartOut(BaseModel):
    """Toàn bộ giỏ của một user."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
    items: list[CartItemOut] = Field(default_factory=list)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def total_quantity(self) -> int:
        """Tổng số lượng món trong giỏ."""
        return sum(item.quantity for item in self.items)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def total_price(self) -> float:
        """Tổng thành tiền của giỏ."""
        total = sum(
            (Decimal(str(item.food.price)) * item.quantity for item in self.items),
            Decimal("0"),
        )
        return _to_money(total)


class CartItemCreate(BaseModel):
    """Body của POST /cart/items: thêm `quantity` món `food_id` vào giỏ.

    Nhận cả "foodId" (FE hay dùng) và "food_id" (kiểu Python) cho tiện.
    """

    food_id: int = Field(ge=1, examples=[1])
    quantity: int = Field(default=1, ge=1, le=99, examples=[2])

    @model_validator(mode="before")
    @classmethod
    def _accept_camel_case(cls, data: Any) -> Any:
        """Đổi foodId -> food_id trước khi kiểm tra dữ liệu."""
        if isinstance(data, dict) and "foodId" in data and "food_id" not in data:
            data = {**data, "food_id": data["foodId"]}
        return data
