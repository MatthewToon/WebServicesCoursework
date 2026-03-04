"""
Genre model.

Represents the gameplay genre of a title
(e.g., Action, Sports, RPG).

Used as a dimension table for aggregation and analytics queries.
"""

from sqlalchemy import Column, Integer, String
from app.db import Base


class Genre(Base):
    __tablename__ = "genres"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(120), nullable=False, unique=True, index=True)
    slug = Column(String(120), nullable=False, unique=True, index=True)