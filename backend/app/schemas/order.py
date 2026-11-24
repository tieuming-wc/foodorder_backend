from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    item_id: int
    item_name: str
    quantity: int
    unit_price: float
    total_price: float


class OrderItemCreate(BaseModel):
    item_id: int = Field(gt=0)
    quantity: int = Field(ge=1, le=99)


class OrderCreate(BaseModel):
    recipient_name: str = Field(min_length=1, max_length=150)
    phone_number: str = Field(pattern=r"^0\d{9}$")
    address_line: str = Field(min_length=5)
    note: str | None = Field(default=None, max_length=500)
    coupon_code: str | None = Field(default=None, max_length=50)
    payment_method: str = Field(default="cod", pattern=r"^(cod|bank)$")
    items: list[OrderItemCreate] = Field(min_length=1, max_length=50)


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    recipient_name: str
    phone_number: str
    address_line: str
    note: str | None
    subtotal: float
    shipping_fee: float
    discount_amount: float
    coupon_code: str | None
    total_amount: float
    payment_method: str
    payment_status: str
    status: str
    created_at: datetime
    items: list[OrderItemOut]
