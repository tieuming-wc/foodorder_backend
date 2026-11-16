"""Đọc cấu hình từ file .env (hoặc biến môi trường).

Muốn thêm cấu hình mới: thêm 1 dòng vào class Settings + thêm vào .env.example.
"""
from pathlib import Path
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/app/core/config.py -> parents[2] = thư mục backend/ (nơi để file .env)
PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    # Tìm .env bằng đường dẫn tuyệt đối nên chạy server từ thư mục nào cũng đọc được
    # backend/.env. Nếu ngay tại thư mục đang đứng có file .env riêng thì file đó
    # được ưu tiên (đứng sau trong danh sách).
    model_config = SettingsConfigDict(
        env_file=(PROJECT_ROOT / ".env", ".env"),
        env_file_encoding="utf-8",
    )

    APP_NAME: str = "KS25 Base API"

    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "app_db"

    # Chuỗi các origin cách nhau bằng dấu phẩy, hoặc "*"
    CORS_ORIGINS: str = "*"

    # ---- Đăng nhập bằng token ----
    # Khoá bí mật để ký token. Đổi khoá này thì mọi token cũ mất hiệu lực.
    # Sinh khoá mới: python -c "import secrets;print(secrets.token_hex(32))"
    SECRET_KEY: str = "doi-khoa-nay-truoc-khi-deploy-that"
    # Token hết hạn sau bao nhiêu phút -> hết hạn thì FE phải đăng nhập lại
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    @property
    def database_url(self) -> str:
        # mysql+pymysql://user:password@host:port/database
        # quote_plus: để mật khẩu có ký tự đặc biệt (@, #, /...) không làm hỏng URL
        return (
            f"mysql+pymysql://{self.DB_USER}:{quote_plus(self.DB_PASSWORD)}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
        )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
