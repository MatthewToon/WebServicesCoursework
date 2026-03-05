"""
Common response schemas.

Shared models used across multiple endpoints, such as pagination metadata.
Keeping these in one module avoids duplication and keeps schemas consistent.
"""

from pydantic import BaseModel, Field


class PageMeta(BaseModel):
    page: int = Field(..., example=1, description="Current page number (1-indexed).")
    page_size: int = Field(..., example=25, description="Number of items requested per page.")
    total: int = Field(..., example=500, description="Total number of matching items.")