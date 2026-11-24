from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Import các session, model và schema theo cấu trúc tương đối
from app.db.session import SessionLocal, Base
from app.models.cart import Cart, CartItem
from app.models.food import Food
from app.models.order import Order, OrderItem
from app.schemas.order import OrderCreate, OrderResponse

# Hàm dependency lấy database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Hàm dependency lấy thông tin người dùng hiện tại (giả lập hoặc tích hợp sẵn hệ thống auth)
def get_current_user(db: Session = Depends(get_db)):
    class MockUser:
        id = 1
    return MockUser()

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order_in: OrderCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    # Lấy user_id thực tế từ đối tượng người dùng
    user_id = current_user.id if hasattr(current_user, 'id') else current_user

    # 1. Lấy giỏ hàng của user từ cơ sở dữ liệu
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart or not cart.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Giỏ hàng của bạn đang trống"
        )

    # 2. Sử dụng Database Transaction để đảm bảo tính toàn vẹn dữ liệu
    try:
        total_amount = 0.0
        order_items_to_create = []

        for cart_item in cart.items:
            # Lấy thông tin món ăn từ bảng Food
            food = db.query(Food).filter(Food.id == cart_item.food_id).first()
            if not food:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Sản phẩm ID {cart_item.food_id} không tồn tại"
                )
            
            # Kiểm tra nếu món ăn đã ngừng kinh doanh (is_active == False)
            if hasattr(food, 'is_active') and not food.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Món '{food.name}' đã ngừng kinh doanh, không thể đặt hàng"
                )

            # Tính toán lại giá tiền tại server theo giá hiện tại của sản phẩm
            item_total = float(food.price) * cart_item.quantity
            total_amount += item_total

            # Lưu lại thông tin chi tiết từng sản phẩm trong đơn hàng
            order_items_to_create.append({
                "food_id": food.id,
                "quantity": cart_item.quantity,
                "unit_price": float(food.price),
                "total_price": item_total
            })

        # 3. Tạo bản ghi đơn hàng chính (Order)
        new_order = Order(
            user_id=user_id,
            recipient_name=order_in.recipient_name,
            phone_number=order_in.phone_number,
            address_line=order_in.address_line,
            total_amount=total_amount,
            status="PENDING",
            note=order_in.note
        )
        db.add(new_order)
        db.flush() # Flush để lấy ID của đơn hàng phục vụ việc tạo OrderItem bên dưới

        # 4. Tạo các bản ghi chi tiết đơn hàng (OrderItem)
        for item_data in order_items_to_create:
            order_item = OrderItem(
                order_id=new_order.id,
                **item_data
            )
            db.add(order_item)

        # 5. Xóa sạch các món hàng trong giỏ hàng (CartItem) sau khi tạo đơn thành công
        db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()

        # Hoàn tất transaction (Commit)
        db.commit()
        db.refresh(new_order)
        return new_order

    except Exception as e:
        # Rollback toàn bộ transaction nếu có bất kỳ lỗi nào xảy ra trong quá trình xử lý
        db.rollback()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống khi tạo đơn hàng: {str(e)}"
        )