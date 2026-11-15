-- Thêm cột users.is_admin (0 = user thường, 1 = admin) cho database đã tạo trước đó.
-- Chạy bằng MySQL Workbench: File > Open SQL Script... > chọn file này > bấm tia sét (Execute).
-- Chạy lại nhiều lần không lỗi: cột đã có thì bỏ qua.
-- (MySQL 8 không có ALTER TABLE ... ADD COLUMN IF NOT EXISTS nên phải kiểm tra trước.)

SET NAMES utf8mb4;
USE app_db;

SET @col_exists := (
  SELECT COUNT(*) FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = 'app_db' AND TABLE_NAME = 'users' AND COLUMN_NAME = 'is_admin'
);
SET @sql := IF(
  @col_exists = 0,
  'ALTER TABLE users ADD COLUMN is_admin TINYINT(1) NOT NULL DEFAULT 0 AFTER is_active',
  'SELECT 1'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Cấp quyền admin cho 1 tài khoản: đăng ký trước bằng API rồi đổi username ở dưới.
-- UPDATE users SET is_admin = 1 WHERE username = 'admin';
