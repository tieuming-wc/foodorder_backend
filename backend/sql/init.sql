-- Chay file nay mot lan trong MySQL Workbench de tao database ban dau.
-- Backend se tu tao cac bang con lai, them cot thuc don con thieu va nap mon mau.

SET NAMES utf8mb4;

CREATE DATABASE IF NOT EXISTS app_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE app_db;

CREATE TABLE IF NOT EXISTS items (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  name          VARCHAR(255) NOT NULL,
  description   TEXT NULL,
  price         DECIMAL(12, 2) NOT NULL DEFAULT 0,
  category      VARCHAR(100) NOT NULL DEFAULT 'Món chính',
  image_url     VARCHAR(500) NULL,
  delivery_time VARCHAR(50) NOT NULL DEFAULT '25–35 phút',
  rating        DECIMAL(3, 1) NOT NULL DEFAULT 0,
  is_available  BOOLEAN NOT NULL DEFAULT TRUE,
  created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS users (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  full_name       VARCHAR(150) NOT NULL,
  phone           VARCHAR(30) NULL,
  email           VARCHAR(255) NOT NULL,
  hashed_password VARCHAR(255) NOT NULL,
  role            VARCHAR(30) NOT NULL DEFAULT 'customer',
  is_active       BOOLEAN NOT NULL DEFAULT TRUE,
  created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT uq_users_email UNIQUE (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
