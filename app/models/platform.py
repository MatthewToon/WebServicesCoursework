"""
Platform model.

Represents the gaming platform a title was released on
(e.g., PlayStation 2, Xbox 360, Wii).

This table is a dimension table referenced by the games fact table.
"""

from sqlalchemy import Column, Integer, String
from app.db import Base


class Platform(Base):
    __tablename__ = "platforms"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(120), nullable=False, unique=True, index=True)
    slug = Column(String(120), nullable=False, unique=True, index=True)