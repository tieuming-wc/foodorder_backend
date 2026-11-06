# FoodOrder Project - Tài liệu thiết kế CSDL (Database Design)

Tài liệu này ghi lại chi tiết cấu trúc các bảng thuộc module Database của dự án **FoodOrder**, bao gồm các trường dữ liệu, khóa chính, khóa ngoại và mối quan hệ giữa các bảng[cite: 1].

---

## 1. Danh sách các bảng và cấu trúc chi tiết

### Bảng `users` (Quản lý người dùng)

- `id`: `INT` (Primary Key, Auto Increment) - Mã người dùng
- `name`: `VARCHAR(255)` - Tên người dùng
- `email`: `VARCHAR(255)` (Unique) - Email đăng nhập
- `password`: `VARCHAR(255)` - Mật khẩu đã mã hóa
- `phone`: `VARCHAR(20)` - Số điện thoại liên hệ
- `created_at` / `updated_at`: `DATETIME` - Thời gian tạo và cập nhật

### Bảng `addresses` (Địa chỉ giao hàng)

- `id`: `INT` (Primary Key, Auto Increment) - Mã địa chỉ
- `user_id`: `INT` (Foreign Key trỏ tới `users.id`) - Mã người dùng sở hữu địa chỉ
- `address_line`: `TEXT` - Địa chỉ chi tiết (số nhà, đường, phường/xã,...)

### Bảng `categories` (Danh mục món ăn)

- `id`: `INT` (Primary Key, Auto Increment) - Mã danh mục
- `name`: `VARCHAR(255)` - Tên danh mục (Ví dụ: Đồ ăn, Nước uống, Tráng miệng,...)
- `description`: `TEXT` - Mô tả danh mục

### Bảng `foods` (Món ăn / Sản phẩm)

- `id`: `INT` (Primary Key, Auto Increment) - Mã món ăn
- `category_id`: `INT` (Foreign Key trỏ tới `categories.id`) - Thuộc danh mục nào
- `name`: `VARCHAR(255)` - Tên món ăn
- `description`: `TEXT` - Mô tả chi tiết món ăn
- `price`: `DECIMAL(12, 2)` - Giá tiền
- `image_url`: `VARCHAR(255)` - Đường dẫn hình ảnh minh họa

### Bảng `carts` (Giỏ hàng)

- `id`: `INT` (Primary Key, Auto Increment) - Mã giỏ hàng
- `user_id`: `INT` (Foreign Key trỏ tới `users.id`) - Chủ sở hữu giỏ hàng

### Bảng `cart_items` (Chi tiết giỏ hàng)

- `id`: `INT` (Primary Key, Auto Increment) - Mã mục giỏ hàng
- `cart_id`: `INT` (Foreign Key trỏ tới `carts.id`) - Thuộc giỏ hàng nào
- `food_id`: `INT` (Foreign Key trỏ tới `foods.id`) - Món ăn được chọn
- `quantity`: `INT` - Số lượng món ăn trong giỏ

### Bảng `vouchers` (Mã giảm giá)

- `id`: `INT` (Primary Key, Auto Increment) - Mã voucher
- `code`: `VARCHAR(50)` (Unique) - Ký tự mã giảm giá (Ví dụ: SALE50)
- `discount_amount`: `DECIMAL(12, 2)` - Số tiền hoặc phần trăm giảm giá
- `expiration_date`: `DATETIME` - Ngày hết hạn

### Bảng `orders` (Đơn hàng)

- `id`: `INT` (Primary Key, Auto Increment) - Mã đơn hàng
- `user_id`: `INT` (Foreign Key trỏ tới `users.id`) - Người đặt hàng
- `address_id`: `INT` (Foreign Key trỏ tới `addresses.id`) - Địa chỉ giao hàng
- `voucher_id`: `INT` (Foreign Key tùy chọn trỏ tới `vouchers.id`) - Mã giảm giá áp dụng
- `total_price`: `DECIMAL(12, 2)` - Tổng giá trị thanh toán
- `status`: `VARCHAR(50)` - Trạng thái đơn hàng (Pending, Shipping, Completed, Cancelled)
- `created_at`: `DATETIME` - Thời gian tạo đơn

### Bảng `order_items` (Chi tiết đơn hàng)

- `id`: `INT` (Primary Key, Auto Increment) - Mã chi tiết đơn hàng
- `order_id`: `INT` (Foreign Key trỏ tới `orders.id`) - Thuộc đơn hàng nào
- `food_id`: `INT` (Foreign Key trỏ tới `foods.id`) - Món ăn trong đơn
- `quantity`: `INT` - Số lượng đặt
- `price`: `DECIMAL(12, 2)` - Giá của món ăn tại thời điểm đặt hàng

---

## 2. Mối quan hệ giữa các bảng (ERD Relations)

- **`users` 1 - n `addresses`**: Một người dùng có thể lưu nhiều địa chỉ giao hàng.
- **`categories` 1 - n `foods`**: Một danh mục chứa nhiều món ăn.
- **`users` 1 - 1 `carts`**: Mỗi người dùng có một giỏ hàng riêng.
- **`carts` 1 - n `cart_items`**: Một giỏ hàng chứa nhiều sản phẩm chi tiết.
- **`foods` 1 - n `cart_items`**: Một món ăn có thể nằm trong giỏ hàng của nhiều người.
- **`users` 1 - n `orders`**: Một người dùng có thể tạo nhiều đơn hàng.
- **`addresses` 1 - n `orders`**: Một địa chỉ có thể được dùng cho nhiều đơn hàng.
- **`vouchers` 1 - n `orders`**: Một mã giảm giá có thể được áp dụng cho nhiều đơn hàng.
- **`orders` 1 - n `order_items`**: Một đơn hàng bao gồm nhiều sản phẩm chi tiết.
- **`foods` 1 - n `order_items`**: Một món ăn có thể xuất hiện trong nhiều chi tiết đơn hàng khác nhau.
