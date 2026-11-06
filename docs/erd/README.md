# ERD — Website đặt món ăn trực tuyến

Sơ đồ thực thể – quan hệ (ERD) cho backend trong repo này: **11 bảng, 14 quan hệ**.

| File | Dùng để |
|---|---|
| `erd.drawio` | Mở bằng [draw.io](https://app.diagrams.net) hoặc draw.io Desktop. **Trang 1**: sơ đồ chỉnh sửa được; **Trang 2**: ảnh render (nhúng sẵn, không cần file ngoài) |
| `erd.png` | Ảnh sơ đồ để dán vào báo cáo / slide / mô tả task |

## Quy ước

- Mọi bảng dùng khóa chính `id INT AUTO_INCREMENT`.
- Khóa ngoại đặt tên `<bảng>_id` (ví dụ `orders.user_id` → `users.id`).
- Đường nối kiểu crow's foot: **đầu gạch = phía 1**, **chân vịt = phía N** (chân vịt nằm ở bảng chứa khóa ngoại).
- `users — carts` là quan hệ **1–1** vì `carts.user_id` có `UNIQUE`.

## Các bảng

| Nhóm | Bảng | Nội dung chính |
|---|---|---|
| Người dùng | `users` | tài khoản, `role` (customer/admin), `status` |
| | `addresses` | sổ địa chỉ giao hàng, cờ `is_default` |
| | `vouchers` | mã giảm giá: `discount_amount`, `min_order_value`, số lượng, thời hạn |
| Danh mục món | `categories` | danh mục, cờ `is_active` |
| | `foods` | món ăn: `category_id`, giá, tồn kho, ảnh, cờ `is_available` |
| Giỏ hàng | `carts` | mỗi người dùng một giỏ (`user_id` UNIQUE) |
| | `cart_items` | món trong giỏ + `quantity` |
| Đơn hàng | `orders` | người đặt, địa chỉ nhận, voucher, `total_price`, `discount_amount`, `status` |
| | `order_items` | dòng đơn: `quantity` + `unit_price` (giá chốt tại thời điểm mua) |
| | `payments` | các lần thanh toán của đơn: phương thức, số tiền, mã giao dịch |
| Đánh giá | `reviews` | đánh giá theo bộ ba (người dùng, món, đơn đã mua), `rating` 1–5 |

## Quan hệ

| Bảng cha (1) | Bảng con (N) | Khóa ngoại |
|---|---|---|
| `users` | `addresses` | `addresses.user_id` |
| `users` | `carts` | `carts.user_id` (1–1, UNIQUE) |
| `users` | `orders` | `orders.user_id` |
| `users` | `reviews` | `reviews.user_id` |
| `categories` | `foods` | `foods.category_id` |
| `foods` | `cart_items` | `cart_items.food_id` |
| `carts` | `cart_items` | `cart_items.cart_id` |
| `foods` | `order_items` | `order_items.food_id` |
| `orders` | `order_items` | `order_items.order_id` |
| `orders` | `payments` | `payments.order_id` |
| `orders` | `reviews` | `reviews.order_id` |
| `foods` | `reviews` | `reviews.food_id` |
| `addresses` | `orders` | `orders.address_id` |
| `vouchers` | `orders` | `orders.voucher_id` (NULL được) |

## Ghi chú

- Bảng `items` trong `backend/sql/init.sql` hiện chỉ là **bảng mẫu** của khung backend; ERD này là lược đồ đích của đề tài (bảng món ăn tương ứng là `foods`).
- ERD chưa kèm file DDL: khi bắt đầu code bảng nào thì viết `CREATE TABLE` cho bảng đó trong `backend/sql/` và giữ đúng tên cột/khóa như sơ đồ.
- Muốn xuất lại ảnh: mở `erd.drawio` → **File → Export as → PNG** (nhớ chọn *Include a copy of my diagram* nếu muốn nhúng ảnh vào file).
