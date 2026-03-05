"""
Publishers router.

Provides read-only endpoints for:
- listing publishers (with pagination + search)
- fetching a publisher by slug
- listing games for a publisher (with optional filters)

These endpoints support the core "publisher intelligence" theme by making
publisher resources easy to browse and query before adding analytics.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.deps import get_db
from app.models.publisher import Publisher
from app.models.game import Game
from app.models.platform import Platform
from app.models.genre import Genre

from app.schemas.publisher import PublisherListOut, PublisherOut
from app.schemas.game import GameListOut, GameOut
from app.schemas.common import PageMeta


router = APIRouter(prefix="/publishers", tags=["publishers"])


@router.get(
    "",
    response_model=PublisherListOut,
    summary="List publishers",
    description="Returns a paginated list of publishers. Supports basic search by name.",
)
def list_publishers(
    q: str | None = Query(default=None, description="Case-insensitive search against publisher name."),
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)."),
    page_size: int = Query(default=25, ge=1, le=100, description="Items per page."),
    db: Session = Depends(get_db),
):
    query = db.query(Publisher)

    if q:
        query = query.filter(func.lower(Publisher.name).contains(q.lower()))

    total = query.count()
    items = (
        query.order_by(Publisher.name.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return PublisherListOut(
        items=items,
        meta=PageMeta(page=page, page_size=page_size, total=total),
    )


@router.get(
    "/{slug}",
    response_model=PublisherOut,
    summary="Get publisher",
    description="Fetch a single publisher by slug.",
    responses={404: {"description": "Publisher not found"}},
)
def get_publisher(
    slug: str,
    db: Session = Depends(get_db),
):
    publisher = db.query(Publisher).filter(Publisher.slug == slug).first()
    if not publisher:
        raise HTTPException(status_code=404, detail="Publisher not found")
    return publisher


@router.get(
    "/{slug}/games",
    response_model=GameListOut,
    summary="List publisher games",
    description="Returns games released by a publisher. Supports filters and pagination.",
    responses={404: {"description": "Publisher not found"}},
)
def list_publisher_games(
    slug: str,
    year: int | None = Query(default=None, description="Filter by release year."),
    platform: str | None = Query(default=None, description="Filter by platform slug."),
    genre: str | None = Query(default=None, description="Filter by genre slug."),
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)."),
    page_size: int = Query(default=25, ge=1, le=100, description="Items per page."),
    db: Session = Depends(get_db),
):
    publisher = db.query(Publisher).filter(Publisher.slug == slug).first()
    if not publisher:
        raise HTTPException(status_code=404, detail="Publisher not found")

    query = (
        db.query(Game)
        .filter(Game.publisher_id == publisher.id)
    )

    if year is not None:
        query = query.filter(Game.year == year)

    if platform is not None:
        query = query.join(Platform, Game.platform_id == Platform.id).filter(Platform.slug == platform)

    if genre is not None:
        query = query.join(Genre, Game.genre_id == Genre.id).filter(Genre.slug == genre)

    total = query.count()
    items = (
        query.order_by(Game.global_sales.desc(), Game.name.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return GameListOut(
        items=items,
        meta=PageMeta(page=page, page_size=page_size, total=total),
    )