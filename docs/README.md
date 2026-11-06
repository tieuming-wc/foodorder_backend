# 🍔 FoodOrder Project - Database Documentation

Tài liệu đặc tả kiến trúc cơ sở dữ liệu và sơ đồ thực thể mối quan hệ (ERD) cho module Backend của dự án[cite: 1].

---

## 📊 1. Tổng quan cấu trúc các bảng (Schema Tables)

### 👤 Bảng `users` (Người dùng)

| Khóa / Trường               | Kiểu dữ liệu   | Ràng buộc                 | Mô tả                    |
| :-------------------------- | :------------- | :------------------------ | :----------------------- |
| `id`                        | `INT`          | PK, Auto Increment        | Mã định danh người dùng  |
| `name`                      | `VARCHAR(255)` | NOT NULL                  | Họ và tên                |
| `email`                     | `VARCHAR(255)` | UNIQUE, NOT NULL          | Thư điện tử đăng nhập    |
| `password`                  | `VARCHAR(255)` | NOT NULL                  | Mật khẩu (đã mã hóa)     |
| `phone`                     | `VARCHAR(20)`  | -                         | Số điện thoại            |
| `created_at` / `updated_at` | `DATETIME`     | DEFAULT CURRENT_TIMESTAMP | Thời gian tạo / cập nhật |

### 📍 Bảng `addresses` (Địa chỉ giao hàng)

| Khóa / Trường  | Kiểu dữ liệu | Ràng buộc          | Mô tả                                |
| :------------- | :----------- | :----------------- | :----------------------------------- |
| `id`           | `INT`        | PK, Auto Increment | Mã địa chỉ                           |
| `user_id`      | `INT`        | FK (`users.id`)    | Mã người dùng sở hữu                 |
| `address_line` | `TEXT`       | NOT NULL           | Địa chỉ chi tiết (số nhà, đường,...) |

### 📂 Bảng `categories` (Danh mục món ăn)

| Khóa / Trường | Kiểu dữ liệu   | Ràng buộc          | Mô tả                              |
| :------------ | :------------- | :----------------- | :--------------------------------- |
| `id`          | `INT`          | PK, Auto Increment | Mã danh mục                        |
| `name`        | `VARCHAR(255)` | NOT NULL           | Tên danh mục (Đồ ăn, Thức uống...) |
| `description` | `TEXT`         | -                  | Mô tả chi tiết danh mục            |

### 🍲 Bảng `foods` (Sản phẩm / Món ăn)

| Khóa / Trường | Kiểu dữ liệu     | Ràng buộc            | Mô tả                       |
| :------------ | :--------------- | :------------------- | :-------------------------- |
| `id`          | `INT`            | PK, Auto Increment   | Mã món ăn                   |
| `category_id` | `INT`            | FK (`categories.id`) | Thuộc danh mục nào          |
| `name`        | `VARCHAR(255)`   | NOT NULL             | Tên món ăn                  |
| `description` | `TEXT`           | -                    | Mô tả nguyên liệu, hương vị |
| `price`       | `DECIMAL(12, 2)` | NOT NULL             | Giá bán niêm yết            |
| `image_url`   | `VARCHAR(255)`   | -                    | Link ảnh minh họa           |

### 🛒 Bảng `carts` (Giỏ hàng)

| Khóa / Trường | Kiểu dữ liệu | Ràng buộc               | Mô tả               |
| :------------ | :----------- | :---------------------- | :------------------ |
| `id`          | `INT`        | PK, Auto Increment      | Mã giỏ hàng         |
| `user_id`     | `INT`        | FK (`users.id`), UNIQUE | Chủ sở hữu giỏ hàng |

### 📦 Bảng `cart_items` (Chi tiết giỏ hàng)

| Khóa / Trường | Kiểu dữ liệu | Ràng buộc           | Mô tả                |
| :------------ | :----------- | :------------------ | :------------------- |
| `id`          | `INT`        | PK, Auto Increment  | Mã chi tiết giỏ hàng |
| `cart_id`     | `INT`        | FK (`carts.id`)     | Thuộc giỏ hàng nào   |
| `food_id`     | `INT`        | FK (`foods.id`)     | Món ăn được thêm vào |
| `quantity`    | `INT`        | NOT NULL, DEFAULT 1 | Số lượng đặt         |

### 🎟️ Bảng `vouchers` (Mã giảm giá)

| Khóa / Trường     | Kiểu dữ liệu     | Ràng buộc          | Mô tả                              |
| :---------------- | :--------------- | :----------------- | :--------------------------------- |
| `id`              | `INT`            | PK, Auto Increment | Mã voucher                         |
| `code`            | `VARCHAR(50)`    | UNIQUE, NOT NULL   | Ký tự mã giảm (VD: SALE50)         |
| `discount_amount` | `DECIMAL(12, 2)` | NOT NULL           | Giá trị giảm (tiền hoặc phần trăm) |
| `expiration_date` | `DATETIME`       | NOT NULL           | Thời hạn sử dụng                   |

### 📋 Bảng `orders` (Đơn hàng)

| Khóa / Trường | Kiểu dữ liệu     | Ràng buộc                    | Mô tả                                                |
| :------------ | :--------------- | :--------------------------- | :--------------------------------------------------- |
| `id`          | `INT`            | PK, Auto Increment           | Mã đơn hàng                                          |
| `user_id`     | `INT`            | FK (`users.id`)              | Khách hàng đặt                                       |
| `address_id`  | `INT`            | FK (`addresses.id`)          | Địa chỉ nhận hàng                                    |
| `voucher_id`  | `INT`            | FK (`vouchers.id`), NULLABLE | Mã giảm giá áp dụng                                  |
| `total_price` | `DECIMAL(12, 2)` | NOT NULL                     | Tổng tiền thanh toán                                 |
| `status`      | `VARCHAR(50)`    | DEFAULT 'Pending'            | Trạng thái (Pending, Shipping, Completed, Cancelled) |
| `created_at`  | `DATETIME`       | DEFAULT CURRENT_TIMESTAMP    | Thời điểm tạo đơn                                    |

### 📑 Bảng `order_items` (Chi tiết đơn hàng)

| Khóa / Trường | Kiểu dữ liệu     | Ràng buộc          | Mô tả                 |
| :------------ | :--------------- | :----------------- | :-------------------- |
| `id`          | `INT`            | PK, Auto Increment | Mã dòng chi tiết đơn  |
| `order_id`    | `INT`            | FK (`orders.id`)   | Thuộc đơn hàng nào    |
| `food_id`     | `INT`            | FK (`foods.id`)    | Món ăn trong đơn      |
| `quantity`    | `INT`            | NOT NULL           | Số lượng mua          |
| `price`       | `DECIMAL(12, 2)` | NOT NULL           | Giá tại thời điểm mua |

---

## 🔗 2. Sơ đồ quan hệ thực thể (ERD Relationships)

- **`users` (1) ── (N) `addresses`**: Một tài khoản có thể lưu nhiều địa chỉ giao hàng.
- **`categories` (1) ── (N) `foods`**: Một danh mục chứa nhiều sản phẩm món ăn khác nhau.
- **`users` (1) ── (1) `carts`**: Mỗi người dùng sở hữu một giỏ hàng riêng biệt.
- **`carts` (1) ── (N) `cart_items`**: Giỏ hàng bao gồm nhiều mục sản phẩm khác nhau.
- **`foods` (1) ── (N) `cart_items`**: Một món ăn có thể nằm trong giỏ hàng của nhiều người dùng.
- **`users` (1) ── (N) `orders`**: Một người dùng có thể tạo nhiều lịch sử đơn hàng.
- **`addresses` (1) ── (N) `orders`**: Một địa chỉ có thể được sử dụng cho nhiều đơn hàng khác nhau.
- **`vouchers` (1) ── (N) `orders`**: Một mã giảm giá có thể áp dụng cho nhiều đơn hàng.
- **`orders` (1) ── (N) `order_items`**: Một đơn hàng gồm nhiều món ăn chi tiết.
- **`foods` (1) ── (N) `order_items`**: Một món ăn xuất hiện trong lịch sử nhiều đơn hàng khác nhau.
