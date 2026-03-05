"""
Analytics response schemas.

Defines Pydantic response models for analytical endpoints, such as
publisher hit rate, efficiency, regional bias, and momentum.

These schemas are used to:
- standardise API output
- improve Swagger/OpenAPI documentation
- keep router code simpler and less error-prone
"""

from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


Region = Literal["na", "eu", "jp", "other", "global"]


class PublisherRef(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    slug: str
    name: str


class PublisherScore(BaseModel):
    publisher: PublisherRef
    titles: int = Field(ge=0)
    value: float


class PublisherHitRateOut(BaseModel):
    region: Region
    threshold: float
    min_titles: int
    items: list[PublisherScore]


class PublisherEfficiencyOut(BaseModel):
    metric: Literal["mean", "median"]
    min_titles: int
    items: list[PublisherScore]


class PublisherRegionalBiasItem(BaseModel):
    publisher: PublisherRef
    titles: int = Field(ge=0)
    region_share: float = Field(ge=0, le=1)


class PublisherRegionalBiasOut(BaseModel):
    region: Literal["na", "eu", "jp", "other"]
    min_titles: int
    items: list[PublisherRegionalBiasItem]


class PublisherMomentumItem(BaseModel):
    publisher: PublisherRef
    titles: int = Field(ge=0)
    window_years: int
    last_window_avg: float
    prev_window_avg: float
    momentum: float
    previous_window: tuple[int, int]
    last_window: tuple[int, int]


class PublisherMomentumOut(BaseModel):
    region: Region
    min_titles: int
    items: list[PublisherMomentumItem]