from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    username: str
    email: EmailStr = Field(..., example="user@gmail.com")
    password: str
    full_name: Optional[str] = None
    phone: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr = Field(..., example="user@gmail.com")
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role: str
    status: int

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserListResponse(BaseModel):
    total: int
    items: List[UserOut]


class UpdateRoleRequest(BaseModel):
    role: str


class UpdateStatusRequest(BaseModel):
    status: int
