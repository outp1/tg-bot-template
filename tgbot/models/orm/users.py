from sqlalchemy import Column, String, DateTime

from .base import BaseModel


class UserModel(BaseModel):
    __tablename__ = "users"

    username = Column(String, unique=True)
    ban_date = Column(DateTime, nullable=True)
    unbanned_date = Column(DateTime, nullable=True)
