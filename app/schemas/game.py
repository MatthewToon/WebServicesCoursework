"""
Game response schemas.

This module defines the Pydantic models used to serialize game records
from the database into API responses.

Games represent the central fact table in the dataset and include
both dimensional references (publisher, platform, genre) and
regional sales metrics.

GameOut
    Represents a single game record including sales data and
    foreign key references to related entities.

GameListOut
    Represents a paginated collection of game records with
    accompanying pagination metadata.

These schemas are primarily used by catalogue endpoints such as:

    GET /publishers/{slug}/games

The schemas expose only the fields required by the API while keeping
the underlying SQLAlchemy models internal to the application.
This separation improves maintainability and helps ensure that future
changes to the database schema do not directly affect the public API.
"""

from pydantic import BaseModel
from app.schemas.common import PageMeta

class GameOut(BaseModel):
    id: int
    name: str
    year: int | None

    na_sales: float
    eu_sales: float
    jp_sales: float
    other_sales: float
    global_sales: float

    publisher_id: int
    platform_id: int
    genre_id: int

    class Config:
        from_attributes = True

class GameListOut(BaseModel):
    items: list[GameOut]
    meta: PageMeta