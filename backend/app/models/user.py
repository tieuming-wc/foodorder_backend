from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    
    # Không dùng Optional để né lỗi Python 3.14, dùng trực tiếp str + nullable=True
    phone: Mapped[str] = mapped_column(String(20), nullable=True) 
    password_hash: Mapped[str] = mapped_column(String(255))
    
    role: Mapped[str] = mapped_column(String(20), default="USER") # USER hoặc ADMIN
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())