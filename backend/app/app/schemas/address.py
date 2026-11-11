import re
from typing import Optional
from pydantic import BaseModel, Field, field_validator # Đổi từ validator sang field_validator

class AddressBase(BaseModel):
    recipient_name: str = Field(..., example="Nguyễn Văn A")
    phone_number: str = Field(..., example="0987654321")
    address_line: str = Field(..., example="Số 1 Đại Cồ Việt, Hai Bà Trưng, Hà Nội")
    is_default: Optional[bool] = False

    @field_validator('phone_number')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        pattern = r'^0\d{9}$'
        if not re.match(pattern, v):
            raise ValueError('Số điện thoại không hợp lệ (phải gồm 10 chữ số và bắt đầu bằng số 0)')
        return v

class AddressCreate(AddressBase):
    pass

class AddressUpdate(BaseModel):
    recipient_name: Optional[str] = None
    phone_number: Optional[str] = None
    address_line: Optional[str] = None
    is_default: Optional[bool] = None

    @field_validator('phone_number')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            pattern = r'^0\d{9}$'
            if not re.match(pattern, v):
                raise ValueError('Số điện thoại không hợp lệ')
        return v

class AddressResponse(AddressBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True # Pydantic v2 dùng from_attributes thay cho orm_mode = True