"""Schema = hình dạng dữ liệu đi ra của API đơn hàng.

API tạo đơn do phần đặt hàng làm, ở đây chỉ có lịch sử mua hàng + huỷ đơn.
"""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field

from app.models.order import CANCELABLE_STATUSES


class OrderItemOut(BaseModel):
    """1 dòng hàng trong đơn: tên + giá tại lúc mua, số lượng, thành tiền."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    item_id: int | None
    item_name: str
    unit_price: float
    quantity: int

    @computed_field
    @property
    def subtotal(self) -> float:
        return self.unit_price * self.quantity


class OrderOut(BaseModel):
    """1 đơn hàng trong lịch sử mua hàng. Giá tiền trả về dạng số cho FE dễ dùng."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    total_amount: float
    note: str | None
    created_at: datetime
    updated_at: datetime
    canceled_at: datetime | None
    items: list[OrderItemOut]

    @computed_field
    @property
    def can_cancel(self) -> bool:
        # FE dựa vào đây để ẩn/hiện nút "Huỷ đơn"
        return self.status in CANCELABLE_STATUSES


class CancelOrderOut(BaseModel):
    """Kết quả huỷ đơn: thông báo cho FE + đơn hàng sau khi huỷ."""

    message: str
    order: OrderOut


class AdminOrderCustomer(BaseModel):
    """Thông tin người đặt, để admin biết đơn này của ai (không trả mật khẩu)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    full_name: str | None
    email: str | None
    is_active: bool
    role: str


class AdminOrderOut(OrderOut):
    """1 đơn trong bảng quản lý: đủ chi tiết món + thông tin khách đặt."""

    user_id: int
    user: AdminOrderCustomer
    restaurant_id: int | None
    shipper_id: int | None
    restaurant: AdminOrderCustomer | None
    shipper: AdminOrderCustomer | None


class AdminOrderListOut(BaseModel):
    """Danh sách đơn cho admin, có phân trang."""

    total: int
    page: int
    limit: int
    total_pages: int
    items: list[AdminOrderOut]


class AdminOrderStatusUpdate(BaseModel):
    """Trạng thái admin muốn chuyển đơn sang (Duyệt / Đang giao / Hoàn thành / Đã huỷ)."""

    status: Literal["confirmed", "shipping", "completed", "cancelled"] = Field(
        examples=["confirmed"],
        description="confirmed = duyệt đơn, shipping = đang giao, completed = hoàn thành, cancelled = huỷ đơn",
    )
