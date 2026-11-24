"""Schema = hình dạng dữ liệu đi vào (request) và đi ra (response) của API.

FastAPI dùng schema để tự kiểm tra dữ liệu: sai kiểu / thiếu trường -> trả lỗi 422.
"""
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ItemBase(BaseModel):
    name: str = Field(min_length=1, max_length=255, examples=["Cơm rang"])
    description: str | None = Field(default=None, examples=["Mô tả ngắn"])
    price: Decimal = Field(default=0, ge=0, examples=[45000])
    category: str = Field(default="Món chính", max_length=100)
    image_url: str | None = None
    delivery_time: str = Field(default="25–35 phút", max_length=50)
    rating: Decimal = Field(default=0, ge=0, le=5)
    is_available: bool = True


class ItemCreate(ItemBase):
    """Dữ liệu FE gửi lên khi THÊM mới."""


class ItemUpdate(BaseModel):
    """Dữ liệu FE gửi lên khi SỬA. Trường nào không gửi thì giữ nguyên."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    price: Decimal | None = Field(default=None, ge=0)
    category: str | None = Field(default=None, max_length=100)
    image_url: str | None = None
    delivery_time: str | None = Field(default=None, max_length=50)
    rating: Decimal | None = Field(default=None, ge=0, le=5)
    is_available: bool | None = None


class ItemOut(ItemBase):
    """Dữ liệu API trả về cho FE."""

    # from_attributes: cho phép đọc thẳng từ object SQLAlchemy (item.name, item.price...)
    model_config = ConfigDict(from_attributes=True)

    id: int
    price: float  # trả về dạng số (45000.0) cho FE dễ dùng
    created_at: datetime
    updated_at: datetime


class PopularItemOut(BaseModel):
    item: ItemOut
    sold_quantity: int
