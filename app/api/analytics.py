"""
Analytics module.

Contains analytics functions + API endpoints that compute derived metrics from the
dataset (games fact table + dimension tables). These analytics are read-only and
are used by the Dashboard Renderer to power widgets.

Design goals:
- Keep analytics deterministic and transparent (no "fake AI").
- Keep functions callable from other modules (e.g., renderer dispatch).
- Validate / bound parameters at the API layer.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.game import Game
from app.models.publisher import Publisher
from app.models.genre import Genre
from app.models.platform import Platform

router = APIRouter(prefix="/analytics", tags=["analytics"])


# ---------------------------
# Small helpers
# ---------------------------

def _as_float(x) -> float:
    """Convert DB numeric types (e.g., Decimal) into JSON-friendly float."""
    if x is None:
        return 0.0
    if isinstance(x, Decimal):
        return float(x)
    return float(x)


def _publisher_or_404(db: Session, slug: str) -> Publisher:
    pub = db.query(Publisher).filter(Publisher.slug == slug).first()
    if not pub:
        raise HTTPException(status_code=404, detail="Publisher not found")
    return pub


def _year_filtered_query(q, from_year: int | None, to_year: int | None):
    if from_year is not None:
        q = q.filter(Game.year >= from_year)
    if to_year is not None:
        q = q.filter(Game.year <= to_year)
    return q


# ---------------------------
# 1) Publisher Overview
# ---------------------------

def publisher_overview(
    db: Session,
    publisher_slug: str,
    from_year: int | None = None,
    to_year: int | None = None,
) -> dict:
    """
    Compute a publisher overview for a given time window.

    Returns:
    - total sales by region + global
    - title count
    - top genre (by global sales)
    - top platform (by global sales)
    """
    pub = _publisher_or_404(db, publisher_slug)

    base = db.query(Game).filter(Game.publisher_id == pub.id)
    base = _year_filtered_query(base, from_year, to_year)

    # Totals and count
    totals = (
        base.with_entities(
            func.count(Game.id),
            func.coalesce(func.sum(Game.na_sales), 0),
            func.coalesce(func.sum(Game.eu_sales), 0),
            func.coalesce(func.sum(Game.jp_sales), 0),
            func.coalesce(func.sum(Game.other_sales), 0),
            func.coalesce(func.sum(Game.global_sales), 0),
        )
        .one()
    )

    title_count = int(totals[0])
    na = _as_float(totals[1])
    eu = _as_float(totals[2])
    jp = _as_float(totals[3])
    other = _as_float(totals[4])
    global_sales = _as_float(totals[5])

    # Top genre by global sales
    top_genre_row = (
        db.query(Genre.name, func.coalesce(func.sum(Game.global_sales), 0).label("s"))
        .join(Game, Game.genre_id == Genre.id)
        .filter(Game.publisher_id == pub.id)
    )
    top_genre_row = _year_filtered_query(top_genre_row, from_year, to_year)
    top_genre_row = top_genre_row.group_by(Genre.name).order_by(func.sum(Game.global_sales).desc()).first()

    top_genre = top_genre_row[0] if top_genre_row else None

    # Top platform by global sales
    top_platform_row = (
        db.query(Platform.name, func.coalesce(func.sum(Game.global_sales), 0).label("s"))
        .join(Game, Game.platform_id == Platform.id)
        .filter(Game.publisher_id == pub.id)
    )
    top_platform_row = _year_filtered_query(top_platform_row, from_year, to_year)
    top_platform_row = top_platform_row.group_by(Platform.name).order_by(func.sum(Game.global_sales).desc()).first()

    top_platform = top_platform_row[0] if top_platform_row else None

    return {
        "publisher": {"id": pub.id, "name": pub.name, "slug": pub.slug},
        "window": {"from_year": from_year, "to_year": to_year},
        "title_count": title_count,
        "sales": {
            "na": na,
            "eu": eu,
            "jp": jp,
            "other": other,
            "global": global_sales,
        },
        "top_genre": top_genre,
        "top_platform": top_platform,
    }


@router.get(
    "/publishers/{slug}/overview",
    summary="Publisher overview (sales totals, count, top genre/platform)",
)
def publisher_overview_endpoint(
    slug: str,
    from_year: int | None = Query(default=None, ge=1970, le=2100),
    to_year: int | None = Query(default=None, ge=1970, le=2100),
    db: Session = Depends(get_db),
):
    if from_year is not None and to_year is not None and from_year > to_year:
        raise HTTPException(status_code=422, detail="from_year must be <= to_year")
    return publisher_overview(db=db, publisher_slug=slug, from_year=from_year, to_year=to_year)


# ---------------------------
# 2) Hit rate
# ---------------------------

def publisher_hit_rate(
    db: Session,
    threshold: float = 1.0,
    min_titles: int = 10,
    region: Literal["na", "eu", "jp", "other", "global"] = "global",
    limit: int = 50,
) -> dict:
    """
    Hit rate leaderboard:
    percentage of a publisher's titles with sales >= threshold (in the chosen region).
    """
    sales_col = {
        "na": Game.na_sales,
        "eu": Game.eu_sales,
        "jp": Game.jp_sales,
        "other": Game.other_sales,
        "global": Game.global_sales,
    }[region]

    # Count total titles per publisher and "hits" per publisher
    total_q = (
        db.query(Game.publisher_id.label("publisher_id"), func.count(Game.id).label("total"))
        .group_by(Game.publisher_id)
        .subquery()
    )

    hits_q = (
        db.query(Game.publisher_id.label("publisher_id"), func.count(Game.id).label("hits"))
        .filter(sales_col >= threshold)
        .group_by(Game.publisher_id)
        .subquery()
    )

    rows = (
        db.query(
            Publisher.slug,
            Publisher.name,
            total_q.c.total,
            func.coalesce(hits_q.c.hits, 0).label("hits"),
        )
        .join(total_q, total_q.c.publisher_id == Publisher.id)
        .outerjoin(hits_q, hits_q.c.publisher_id == Publisher.id)
        .filter(total_q.c.total >= min_titles)
        .limit(limit)
        .all()
    )

    items = []
    for slug, name, total, hits in rows:
        total_i = int(total)
        hits_i = int(hits)
        rate = (hits_i / total_i) if total_i else 0.0
        items.append({"slug": slug, "name": name, "total_titles": total_i, "hits": hits_i, "hit_rate": rate})

    items.sort(key=lambda x: x["hit_rate"], reverse=True)

    return {
        "threshold": threshold,
        "min_titles": min_titles,
        "region": region,
        "items": items,
    }


@router.get("/publisher-hit-rate", summary="Publisher hit rate leaderboard")
def publisher_hit_rate_endpoint(
    threshold: float = Query(1.0, ge=0),
    min_titles: int = Query(10, ge=1),
    region: Literal["na", "eu", "jp", "other", "global"] = Query("global"),
    db: Session = Depends(get_db),
):
    return publisher_hit_rate(db=db, threshold=threshold, min_titles=min_titles, region=region)


# ---------------------------
# 3) Sales efficiency
# ---------------------------

def publisher_efficiency(
    db: Session,
    metric: Literal["mean", "median"] = "mean",
    min_titles: int = 10,
    limit: int = 50,
) -> dict:
    """
    Sales efficiency ranking:
    average (mean/median) global sales per title for each publisher.
    """
    # Mean is simple in SQL. Median is trickier; we implement median using percentile_cont.
    if metric == "mean":
        q = (
            db.query(
                Publisher.slug,
                Publisher.name,
                func.count(Game.id).label("total"),
                func.coalesce(func.avg(Game.global_sales), 0).label("value"),
            )
            .join(Game, Game.publisher_id == Publisher.id)
            .group_by(Publisher.id)
            .having(func.count(Game.id) >= min_titles)
            .limit(limit)
            .all()
        )
        items = [
            {
                "slug": slug,
                "name": name,
                "total_titles": int(total),
                "mean_global_sales": _as_float(value),
            }
            for slug, name, total, value in q
        ]
        items.sort(key=lambda x: x["mean_global_sales"], reverse=True)
        return {"metric": "mean", "min_titles": min_titles, "items": items}

    # Median using PostgreSQL percentile_cont (works in Postgres)
    median_expr = func.percentile_cont(0.5).within_group(Game.global_sales)

    q = (
        db.query(
            Publisher.slug,
            Publisher.name,
            func.count(Game.id).label("total"),
            func.coalesce(median_expr, 0).label("value"),
        )
        .join(Game, Game.publisher_id == Publisher.id)
        .group_by(Publisher.id)
        .having(func.count(Game.id) >= min_titles)
        .limit(limit)
        .all()
    )

    items = [
        {
            "slug": slug,
            "name": name,
            "total_titles": int(total),
            "median_global_sales": _as_float(value),
        }
        for slug, name, total, value in q
    ]
    items.sort(key=lambda x: x["median_global_sales"], reverse=True)
    return {"metric": "median", "min_titles": min_titles, "items": items}


@router.get("/publisher-efficiency", summary="Publisher efficiency ranking")
def publisher_efficiency_endpoint(
    metric: Literal["mean", "median"] = Query("mean"),
    min_titles: int = Query(10, ge=1),
    db: Session = Depends(get_db),
):
    return publisher_efficiency(db=db, metric=metric, min_titles=min_titles)


# ---------------------------
# 4) Regional bias index
# ---------------------------

def publisher_regional_bias(
    db: Session,
    region: Literal["na", "eu", "jp", "other"] = "jp",
    min_titles: int = 10,
    limit: int = 50,
) -> dict:
    """
    Regional bias index:
    (publisher's share of sales in region) / (market share of sales in region)

    Interpreting the number:
    - 1.0 = matches overall market share
    - >1  = over-indexed in that region
    - <1  = under-indexed in that region
    """
    region_col = {"na": Game.na_sales, "eu": Game.eu_sales, "jp": Game.jp_sales, "other": Game.other_sales}[region]

    # Market shares
    market_region = db.query(func.coalesce(func.sum(region_col), 0)).scalar() or 0
    market_global = db.query(func.coalesce(func.sum(Game.global_sales), 0)).scalar() or 0

    if market_global == 0 or market_region == 0:
        return {"region": region, "min_titles": min_titles, "items": []}

    rows = (
        db.query(
            Publisher.slug,
            Publisher.name,
            func.count(Game.id).label("total"),
            func.coalesce(func.sum(region_col), 0).label("region_sales"),
            func.coalesce(func.sum(Game.global_sales), 0).label("global_sales"),
        )
        .join(Game, Game.publisher_id == Publisher.id)
        .group_by(Publisher.id)
        .having(func.count(Game.id) >= min_titles)
        .limit(limit)
        .all()
    )

    market_share = _as_float(market_region) / _as_float(market_global)

    items = []
    for slug, name, total, reg_sales, glob_sales in rows:
        reg_sales_f = _as_float(reg_sales)
        glob_sales_f = _as_float(glob_sales)
        if glob_sales_f <= 0:
            continue

        publisher_share = reg_sales_f / glob_sales_f
        bias = publisher_share / market_share if market_share > 0 else 0.0

        items.append(
            {
                "slug": slug,
                "name": name,
                "total_titles": int(total),
                "publisher_region_share": publisher_share,
                "market_region_share": market_share,
                "bias_index": bias,
            }
        )

    items.sort(key=lambda x: x["bias_index"], reverse=True)
    return {"region": region, "min_titles": min_titles, "items": items}


@router.get("/publisher-regional-bias", summary="Publisher regional bias index")
def publisher_regional_bias_endpoint(
    region: Literal["na", "eu", "jp", "other"] = Query("jp"),
    min_titles: int = Query(10, ge=1),
    db: Session = Depends(get_db),
):
    return publisher_regional_bias(db=db, region=region, min_titles=min_titles)


# ---------------------------
# 5) Momentum
# ---------------------------

def publisher_momentum(
    db: Session,
    window: int = 5,
    region: Literal["na", "eu", "jp", "other", "global"] = "global",
    min_titles: int = 10,
    limit: int = 50,
) -> dict:
    """
    Momentum score:
    avg(last N years) - avg(previous N years) for a publisher (in chosen region).
    """
    sales_col = {
        "na": Game.na_sales,
        "eu": Game.eu_sales,
        "jp": Game.jp_sales,
        "other": Game.other_sales,
        "global": Game.global_sales,
    }[region]

    # Determine max year present (ignore null)
    max_year = db.query(func.max(Game.year)).filter(Game.year.isnot(None)).scalar()
    if max_year is None:
        return {"window": window, "region": region, "min_titles": min_titles, "items": []}

    last_start = int(max_year) - window + 1
    prev_start = int(max_year) - (2 * window) + 1
    prev_end = last_start - 1

    # Build per-publisher averages for each window
    last_q = (
        db.query(
            Game.publisher_id.label("publisher_id"),
            func.coalesce(func.avg(sales_col), 0).label("avg_last"),
        )
        .filter(Game.year >= last_start, Game.year <= int(max_year))
        .group_by(Game.publisher_id)
        .subquery()
    )

    prev_q = (
        db.query(
            Game.publisher_id.label("publisher_id"),
            func.coalesce(func.avg(sales_col), 0).label("avg_prev"),
        )
        .filter(Game.year >= prev_start, Game.year <= prev_end)
        .group_by(Game.publisher_id)
        .subquery()
    )

    # Ensure minimum titles overall (across all years) to keep leaderboard sane
    totals_q = (
        db.query(Game.publisher_id.label("publisher_id"), func.count(Game.id).label("total"))
        .group_by(Game.publisher_id)
        .subquery()
    )

    rows = (
        db.query(
            Publisher.slug,
            Publisher.name,
            totals_q.c.total,
            func.coalesce(last_q.c.avg_last, 0).label("avg_last"),
            func.coalesce(prev_q.c.avg_prev, 0).label("avg_prev"),
        )
        .join(totals_q, totals_q.c.publisher_id == Publisher.id)
        .outerjoin(last_q, last_q.c.publisher_id == Publisher.id)
        .outerjoin(prev_q, prev_q.c.publisher_id == Publisher.id)
        .filter(totals_q.c.total >= min_titles)
        .limit(limit)
        .all()
    )

    items = []
    for slug, name, total, avg_last, avg_prev in rows:
        avg_last_f = _as_float(avg_last)
        avg_prev_f = _as_float(avg_prev)
        items.append(
            {
                "slug": slug,
                "name": name,
                "total_titles": int(total),
                "avg_last_window": avg_last_f,
                "avg_prev_window": avg_prev_f,
                "momentum": avg_last_f - avg_prev_f,
                "window": window,
                "last_window_years": [last_start, int(max_year)],
                "prev_window_years": [prev_start, prev_end],
            }
        )

    items.sort(key=lambda x: x["momentum"], reverse=True)
    return {"window": window, "region": region, "min_titles": min_titles, "items": items}


@router.get("/publisher-momentum", summary="Publisher momentum score")
def publisher_momentum_endpoint(
    window: int = Query(5, ge=1, le=30),
    region: Literal["na", "eu", "jp", "other", "global"] = Query("global"),
    min_titles: int = Query(10, ge=1),
    db: Session = Depends(get_db),
):
    return publisher_momentum(db=db, window=window, region=region, min_titles=min_titles)