from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class OrderItemBase(BaseModel):
    food_id: int
    food_name: str
    price: float
    quantity: int

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemResponse(OrderItemBase):
    id: int
    order_id: int

    class Config:
        orm_mode = True

class OrderBase(BaseModel):
    recipient_name: str
    phone_number: str
    address_line: str
    total_amount: float
    shipping_fee: Optional[float] = 0.00
    discount_amount: Optional[float] = 0.00
    final_amount: float
    customer_note: Optional[str] = None

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class OrderResponse(OrderBase):
    id: int
    user_id: int
    order_status: str
    created_at: datetime
    items: List[OrderItemResponse] = []

    class Config:
        orm_mode = True