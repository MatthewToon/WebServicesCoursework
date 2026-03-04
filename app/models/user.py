"""
User model.

Represents an authenticated user who can create dashboards
and manage saved analytical views.
"""

from sqlalchemy import Column, Integer, String
from app.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)