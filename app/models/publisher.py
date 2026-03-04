"""
Publisher model.

Represents a video game publisher (e.g., Nintendo, EA, Ubisoft).
This table acts as a dimension table in the analytics-oriented schema.

Each publisher has a unique name and a URL-friendly slug used
for clean REST API endpoints (e.g., /publishers/nintendo).
"""

from sqlalchemy import Column, Integer, String
from app.db import Base


class Publisher(Base):
    __tablename__ = "publishers"

    id = Column(Integer, primary_key=True, index=True)

    # Cleaned publisher name from dataset
    name = Column(String(255), nullable=False, unique=True, index=True)

    # URL-friendly identifier used in API endpoints
    slug = Column(String(255), nullable=False, unique=True, index=True)