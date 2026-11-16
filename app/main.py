"""Điểm khởi động của backend.

Chạy được từ 2 thư mục, cả hai đều đọc chung file backend/.env:
    cd backend/       && uvicorn app.main:app --reload
    cd backend/app/   && uvicorn main:app --reload
Tài liệu API tự sinh: http://127.0.0.1:8000/docs
"""
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

# Chạy `uvicorn main:app` trong app/ thì thư mục cha của package `app` chưa có trên
# sys.path -> thêm vào để các import `app.xxx` bên dưới chạy được ở cả 2 cách chạy.
_APP_PARENT_DIR = Path(__file__).resolve().parents[1]
if str(_APP_PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_PARENT_DIR))

import app.models  # noqa: E402,F401 - import để SQLAlchemy biết các bảng
from app.core.config import settings  # noqa: E402
from app.db.migrations import apply_column_migrations  # noqa: E402
from app.db.session import Base, engine  # noqa: E402
from app.routers import auth, health, items, orders  # noqa: E402


def _use_utf8_console() -> None:
    """Console Windows mặc định là cp1252/cp437 -> print tiếng Việt sẽ UnicodeEncodeError.

    Chuyển stdout/stderr sang UTF-8 để các thông báo tiếng Việt bên dưới không làm
    server chết khi khởi động (nhất là lúc không kết nối được MySQL).
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            pass


_use_utf8_console()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Tự tạo các bảng còn thiếu khi server khởi động (bảng đã có thì bỏ qua).
    # create_all KHÔNG thêm cột vào bảng đã tồn tại -> apply_column_migrations lo phần đó.
    try:
        Base.metadata.create_all(bind=engine)
        added_columns = apply_column_migrations(engine)
        if added_columns:
            print(f"[DB] Đã thêm cột còn thiếu: {', '.join(added_columns)}")
        print(f"[DB] Đã kết nối MySQL {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
    except SQLAlchemyError as error:
        print("[DB] KHÔNG kết nối được MySQL! Kiểm tra MySQL đã bật chưa và file .env.")
        if "Unknown database" in str(error):
            print("[DB] Chưa có database -> mở MySQL Workbench, chạy file sql/init.sql")
        print(f"[DB] Chi tiết: {error}")
    yield


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

# CORS: cho phép trang FE (khác cổng/khác domain) gọi được API này
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mọi API đều bắt đầu bằng /api. Thêm router mới thì include ở đây.
app.include_router(health.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(items.router, prefix="/api")
app.include_router(orders.router, prefix="/api")


@app.get("/")
def root():
    return {"message": f"{settings.APP_NAME} đang chạy. Xem tài liệu API tại /docs"}
