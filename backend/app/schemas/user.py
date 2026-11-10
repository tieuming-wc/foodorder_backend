from pydantic import BaseModel, EmailStr
from datetime import datetime

# 1. Schema nhận dữ liệu lúc Đăng ký
class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: str | None = None
    password: str

# 2. Schema nhận dữ liệu lúc Đăng nhập
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# 3. Schema trả về cho Frontend (Tuyệt đối không có trường password_hash)
class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    phone: str | None = None
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True