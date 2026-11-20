"""Schema = hình dạng dữ liệu đi vào/ra của API giỏ hàng (/api/cart).

Giỏ hàng luôn lấy theo user trong token, FE KHÔNG gửi user_id lên.
"""
from pydantic import BaseModel, ConfigDict, Field, computed_field

from app.schemas.item import ItemOut


class CartItemAdd(BaseModel):
    """Thêm 1 món vào giỏ. Món đã có trong giỏ thì cộng dồn số lượng."""

    item_id: int = Field(examples=[1])
    quantity: int = Field(default=1, ge=1, le=99, examples=[2])


class CartItemUpdate(BaseModel):
    """Đổi số lượng của 1 món đã có trong giỏ."""

    quantity: int = Field(ge=1, le=99, examples=[3])


class CartItemOut(BaseModel):
    """1 dòng trong giỏ: thông tin món + số lượng + thành tiền."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    item_id: int
    quantity: int
    item: ItemOut

    @computed_field
    @property
    def subtotal(self) -> float:
        return self.item.price * self.quantity


class CartOut(BaseModel):
    """Toàn bộ giỏ hàng: danh sách món + tổng số lượng + tổng tiền."""

    items: list[CartItemOut]
    total_quantity: int
    total_amount: float
