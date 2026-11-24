"""Điểm khởi động của backend.

Chạy:  uvicorn app.main:app --reload
Tài liệu API tự sinh: http://127.0.0.1:8000/docs
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models  # noqa: F401 - import để SQLAlchemy biết các bảng
from app.bootstrap import initialize_database
from app.core.config import settings
from app.routers import auth, health, items, orders


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    print(f"[DB] Đã kết nối MySQL {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
    yield


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)
app.include_router(auth.router, prefix="/api")

# CORS: cho phép trang FE (khác cổng/khác domain) gọi được API này
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mọi API đều bắt đầu bằng /api. Thêm router mới thì include ở đây.
app.include_router(health.router, prefix="/api")
app.include_router(items.router, prefix="/api")
app.include_router(orders.router, prefix="/api")


@app.get("/")
def root():
    return {"message": f"{settings.APP_NAME} đang chạy. Xem tài liệu API tại /docs"}