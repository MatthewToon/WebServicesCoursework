"""
Game model (fact table).

Represents a single game release in the dataset, including
platform, genre, publisher, and regional/global sales.

This table functions as the central "fact table" in a
star-schema inspired analytics design.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Numeric,
    CheckConstraint,
    Index
)

from sqlalchemy.orm import relationship
from app.db import Base


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(255), nullable=False, index=True)
    year = Column(Integer, nullable=True, index=True)

    publisher_id = Column(Integer, ForeignKey("publishers.id"), nullable=False, index=True)
    platform_id = Column(Integer, ForeignKey("platforms.id"), nullable=False, index=True)
    genre_id = Column(Integer, ForeignKey("genres.id"), nullable=False, index=True)

    na_sales = Column(Numeric(10, 2), nullable=False, default=0)
    eu_sales = Column(Numeric(10, 2), nullable=False, default=0)
    jp_sales = Column(Numeric(10, 2), nullable=False, default=0)
    other_sales = Column(Numeric(10, 2), nullable=False, default=0)
    global_sales = Column(Numeric(10, 2), nullable=False, default=0)

    publisher = relationship("Publisher")
    platform = relationship("Platform")
    genre = relationship("Genre")

    __table_args__ = (
        CheckConstraint("na_sales >= 0"),
        CheckConstraint("eu_sales >= 0"),
        CheckConstraint("jp_sales >= 0"),
        CheckConstraint("other_sales >= 0"),
        CheckConstraint("global_sales >= 0"),
        Index("ix_games_publisher_year", "publisher_id", "year"),
    )