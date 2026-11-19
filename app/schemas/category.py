"""Schema = hình dạng dữ liệu đi vào/ra của API danh mục (/api/categories)."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    name: str = Field(min_length=1, max_length=100, examples=["Cơm"])
    description: str | None = Field(default=None, examples=["Các món cơm"])
    sort_order: int = Field(default=0, ge=0, examples=[1])


class CategoryCreate(CategoryBase):
    """Dữ liệu FE gửi lên khi THÊM danh mục (chỉ admin)."""


class CategoryUpdate(BaseModel):
    """Dữ liệu FE gửi lên khi SỬA danh mục. Trường nào không gửi thì giữ nguyên."""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None
    sort_order: int | None = Field(default=None, ge=0)


class CategoryOut(CategoryBase):
    """Danh mục trả về cho FE (kèm số món để hiển thị lên tab)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    item_count: int = 0
    created_at: datetime
    updated_at: datetime
