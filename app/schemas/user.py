"""Schema = hình dạng dữ liệu đi vào (request) và đi ra (response) của API tài khoản."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserRegister(BaseModel):
    """Dữ liệu FE gửi lên khi ĐĂNG KÝ."""

    username: str = Field(min_length=3, max_length=50, examples=["admin"])
    password: str = Field(min_length=6, max_length=128, examples=["123456"])
    full_name: str | None = Field(default=None, max_length=255, examples=["Nguyễn Văn A"])
    email: str | None = Field(default=None, max_length=255, examples=["a@example.com"])


class UserLogin(BaseModel):
    """Dữ liệu FE gửi lên khi ĐĂNG NHẬP (JSON, không phải form-data của OAuth2)."""

    username: str = Field(examples=["admin"])
    password: str = Field(examples=["123456"])


class UserOut(BaseModel):
    """Thông tin tài khoản trả về cho FE (không bao giờ trả mật khẩu)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    full_name: str | None
    email: str | None
    is_active: bool
    is_admin: bool
    created_at: datetime


class TokenOut(BaseModel):
    """Kết quả đăng nhập: FE lưu access_token và gửi kèm mỗi request."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int  # số giây token còn hiệu lực
    user: UserOut
