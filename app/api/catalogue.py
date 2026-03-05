"""
Catalogue router.

Provides read-only endpoints for "dimension tables" such as genres and
platforms. These are used by other endpoints (e.g., publisher games filters)
and help demonstrate a normalized schema design.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.genre import Genre
from app.models.platform import Platform

from app.schemas.catalogue import GenreListOut, PlatformListOut, GenreOut, PlatformOut


router = APIRouter(tags=["catalogue"])


@router.get(
    "/genres",
    response_model=GenreListOut,
    summary="List genres",
    description="Returns all genres in the dataset, sorted alphabetically.",
)
def list_genres(
    db: Session = Depends(get_db),
):
    items = db.query(Genre).order_by(Genre.name.asc()).all()
    return GenreListOut(items=items)


@router.get(
    "/platforms",
    response_model=PlatformListOut,
    summary="List platforms",
    description="Returns all platforms in the dataset, sorted alphabetically.",
)
def list_platforms(
    db: Session = Depends(get_db),
):
    items = db.query(Platform).order_by(Platform.name.asc()).all()
    return PlatformListOut(items=items)