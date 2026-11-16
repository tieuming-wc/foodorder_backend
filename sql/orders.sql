-- Bảng đơn hàng: orders + order_items (dùng cho API lịch sử mua hàng và huỷ đơn).
-- Chạy bằng MySQL Workbench: File > Open SQL Script... > chọn file này > bấm tia sét (Execute).
-- Chạy lại nhiều lần không lỗi (đã có thì bỏ qua).
-- Ghi chú: server cũng tự tạo 2 bảng này khi khởi động (Base.metadata.create_all),
-- nhưng chạy file này trước để chắc chắn đúng kiểu dữ liệu + khoá ngoại.

SET NAMES utf8mb4;
USE app_db;

-- 1 đơn hàng thuộc về 1 user (users.id).
-- status: pending (Chờ duyệt) / confirmed (Đã xác nhận) / shipping (Đang giao)
--         / completed (Hoàn thành) / cancelled (Đã huỷ)
CREATE TABLE IF NOT EXISTS orders (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  user_id      INT NOT NULL,
  status       VARCHAR(20) NOT NULL DEFAULT 'pending',
  total_amount DECIMAL(12, 2) NOT NULL DEFAULT 0,
  note         TEXT NULL,
  canceled_at  DATETIME NULL,
  created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY idx_orders_user_created (user_id, created_at),
  KEY idx_orders_status (status),
  CONSTRAINT fk_orders_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Các dòng hàng của đơn. Lưu tên + giá tại lúc mua để lịch sử không đổi khi item bị sửa/xoá.
CREATE TABLE IF NOT EXISTS order_items (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  order_id   INT NOT NULL,
  item_id    INT NULL,
  item_name  VARCHAR(255) NOT NULL,
  unit_price DECIMAL(12, 2) NOT NULL DEFAULT 0,
  quantity   INT NOT NULL DEFAULT 1,
  KEY idx_order_items_order (order_id),
  CONSTRAINT fk_order_items_order FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE,
  CONSTRAINT fk_order_items_item FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
