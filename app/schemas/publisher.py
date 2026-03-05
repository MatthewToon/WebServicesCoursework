"""
Publisher response schemas.

Defines the Pydantic models used by publisher endpoints. These schemas
control what fields appear in API responses and improve Swagger documentation
with descriptions and example values.
"""

from pydantic import BaseModel, Field
from typing import List

from app.schemas.common import PageMeta


class PublisherOut(BaseModel):
    id: int = Field(..., example=1, description="Internal numeric identifier.")
    name: str = Field(..., example="Nintendo", description="Canonical publisher name.")
    slug: str = Field(..., example="nintendo", description="URL-safe unique identifier.")

    class Config:
        from_attributes = True


class PublisherListOut(BaseModel):
    items: List[PublisherOut] = Field(..., description="Publishers on the current page.")
    meta: PageMeta = Field(..., description="Pagination metadata for the result set.")