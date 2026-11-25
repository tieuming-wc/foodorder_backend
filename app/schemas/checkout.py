"""Schema = hình dạng dữ liệu của API đặt hàng (checkout).

Luồng: thêm món bằng /api/cart -> gọi POST /api/orders/checkout -> hệ thống tạo đơn
từ giỏ rồi XOÁ các món đó khỏi giỏ.
"""
from pydantic import BaseModel, Field

from app.schemas.order import OrderOut


class CheckoutIn(BaseModel):
    """Dữ liệu FE gửi lên khi bấm "Đặt hàng". Không cần gửi món: hệ thống lấy từ giỏ."""

    note: str | None = Field(default=None, max_length=500, examples=["Giao trước 12h"])


class CheckoutOut(BaseModel):
    """Kết quả đặt hàng: đơn vừa tạo + thông báo cho FE."""

    message: str
    order: OrderOut
    cart_is_cleared: bool = True
