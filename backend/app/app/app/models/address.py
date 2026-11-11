from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base

class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipient_name = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=False)
    address_line = Column(Text, nullable=False)
    is_default = Column(Boolean, default=False)