"""
Catalogue (dimension table) response schemas.

Provides simple list outputs for reference tables like genres and platforms.
These schemas are used by the read-only catalogue endpoints.
"""

from pydantic import BaseModel, Field
from typing import List


class GenreOut(BaseModel):
    id: int = Field(..., example=1, description="Internal numeric identifier.")
    name: str = Field(..., example="Sports", description="Genre name.")
    slug: str = Field(..., example="sports", description="URL-safe unique identifier.")

    class Config:
        from_attributes = True


class PlatformOut(BaseModel):
    id: int = Field(..., example=1, description="Internal numeric identifier.")
    name: str = Field(..., example="Wii", description="Platform name.")
    slug: str = Field(..., example="wii", description="URL-safe unique identifier.")

    class Config:
        from_attributes = True


class GenreListOut(BaseModel):
    items: List[GenreOut] = Field(..., description="All genres (sorted).")


class PlatformListOut(BaseModel):
    items: List[PlatformOut] = Field(..., description="All platforms (sorted).")