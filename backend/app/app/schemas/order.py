from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
import re

class OrderCreate(BaseModel):
    recipient_name: str = Field(..., min_length=1, example="Nguyễn Văn A")
    phone_number: str = Field(..., example="0987654321")
    address_line: str = Field(..., min_length=1, example="Số 1 Đại Cồ Việt, Hà Nội")
    note: Optional[str] = None

    @field_validator('phone_number')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        pattern = r'^0\d{9}$'
        if not re.match(pattern, v):
            raise ValueError('Số điện thoại không hợp lệ (phải gồm 10 chữ số và bắt đầu bằng số 0)')
        return v

class OrderItemResponse(BaseModel):
    id: int
    food_id: int
    quantity: int
    unit_price: float
    total_price: float

    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: int
    user_id: int
    recipient_name: str
    phone_number: str
    address_line: str
    total_amount: float
    status: str
    note: Optional[str] = None
    created_at: datetime
    items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True