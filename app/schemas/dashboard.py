"""
Dashboard schemas.

Dashboards are the user-owned CRUD resource used to satisfy the coursework CRUD
requirement, while dataset-derived analytics remain read-only.

Widgets store configuration in JSON and are validated strictly per widget type
using a discriminated union (Pydantic `discriminator="type"`).
"""

from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field, ConfigDict

from app.schemas.common import PageMeta


# ---------------------------
# Widget parameter models
# ---------------------------

class WidgetBase(BaseModel):
    # Reject unknown fields so widget configs can't silently accept typos.
    model_config = ConfigDict(extra="forbid")
    type: str


class PublisherOverviewWidget(WidgetBase):
    type: Literal["publisher_overview"]
    publisher_slug: str
    from_year: int | None = None
    to_year: int | None = None


class HitRateWidget(WidgetBase):
    type: Literal["publisher_hit_rate"]
    threshold: float = Field(default=1.0, ge=0)
    min_titles: int = Field(default=10, ge=1)
    region: Literal["na", "eu", "jp", "other", "global"] = "global"


class EfficiencyWidget(WidgetBase):
    type: Literal["publisher_efficiency"]
    metric: Literal["mean", "median"] = "mean"
    min_titles: int = Field(default=10, ge=1)


class RegionalBiasWidget(WidgetBase):
    type: Literal["publisher_regional_bias"]
    region: Literal["na", "eu", "jp", "other"] = "jp"
    min_titles: int = Field(default=10, ge=1)


class MomentumWidget(WidgetBase):
    type: Literal["publisher_momentum"]
    window: int = Field(default=5, ge=1, le=30)
    region: Literal["na", "eu", "jp", "other", "global"] = "global"
    min_titles: int = Field(default=10, ge=1)


class PublisherComparisonWidget(WidgetBase):
    type: Literal["publisher_comparison"]
    a_slug: str
    b_slug: str
    from_year: int | None = None
    to_year: int | None = None


# Discriminated union: the `type` field chooses which schema applies.
WidgetParams = Annotated[
    Union[
        PublisherOverviewWidget,
        HitRateWidget,
        EfficiencyWidget,
        RegionalBiasWidget,
        MomentumWidget,
        PublisherComparisonWidget,
    ],
    Field(discriminator="type"),
]


# ---------------------------
# Dashboard CRUD schemas
# ---------------------------

class DashboardCreateIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)


class DashboardUpdateIn(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)


class DashboardOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    name: str
    description: str | None = None


class DashboardListOut(BaseModel):
    items: list[DashboardOut]
    meta: PageMeta


# ---------------------------
# Widget CRUD schemas
# ---------------------------

class WidgetCreateIn(BaseModel):
    # Incoming widget must match one of the known widget models above.
    params: WidgetParams


class WidgetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    dashboard_id: int
    params: WidgetParams