-- Nâng cấp database cũ cho hệ thống 4 vai trò + đơn có nhà hàng/shipper.
-- Chạy bằng MySQL Workbench: File > Open SQL Script... > chọn file này > bấm tia sét.
-- Chạy lại nhiều lần không lỗi (cột đã có thì bỏ qua).
-- (Server cũng tự chạy các ALTER này khi khởi động qua app/db/migrations.py.)

SET NAMES utf8mb4;
USE app_db;

-- users.role: admin / customer / restaurant / shipper
SET @col_exists := (
  SELECT COUNT(*) FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = 'app_db' AND TABLE_NAME = 'users' AND COLUMN_NAME = 'role'
);
SET @sql := IF(
  @col_exists = 0,
  "ALTER TABLE users ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'customer' AFTER is_admin",
  'SELECT 1'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- orders.restaurant_id: nhà hàng xử lý đơn
SET @col_exists := (
  SELECT COUNT(*) FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = 'app_db' AND TABLE_NAME = 'orders' AND COLUMN_NAME = 'restaurant_id'
);
SET @sql := IF(
  @col_exists = 0,
  'ALTER TABLE orders ADD COLUMN restaurant_id INT NULL AFTER user_id',
  'SELECT 1'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- orders.shipper_id: shipper nhận giao đơn
SET @col_exists := (
  SELECT COUNT(*) FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = 'app_db' AND TABLE_NAME = 'orders' AND COLUMN_NAME = 'shipper_id'
);
SET @sql := IF(
  @col_exists = 0,
  'ALTER TABLE orders ADD COLUMN shipper_id INT NULL AFTER restaurant_id',
  'SELECT 1'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Tài khoản demo do seed.py tạo (chạy lại seed để đủ 10 tài khoản).
-- Đổi vai trò thủ công nếu cần (nhớ đặt is_admin = 1 cho tài khoản admin):
-- UPDATE users SET role = 'admin', is_admin = 1 WHERE username = 'admin';
