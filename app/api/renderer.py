"""
Dashboard renderer router.

Turns user-saved dashboard widgets into computed analytics outputs.

This is the "integration" layer that makes dashboards functional:
- widgets are stored as validated JSON (per widget type)
- renderer executes the appropriate analytics query for each widget
- output is returned as a list of widget results

This endpoint is JWT-protected because it accesses user-owned resources.
"""

from __future__ import annotations

from pydantic import TypeAdapter

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.dashboard import Dashboard
from app.models.dashboard_widget import DashboardWidget
from app.schemas.dashboard import WidgetParams

# Reuse analytics logic by importing the callable endpoint functions.
# (We call these directly with a DB session to avoid HTTP-to-HTTP calls.)
from app.api.analytics import (
    publisher_overview,
    publisher_hit_rate,
    publisher_efficiency,
    publisher_regional_bias,
    publisher_momentum,
)

router = APIRouter(prefix="/dashboards", tags=["renderer"])


@router.get(
    "/{dashboard_id}/render",
    summary="Render a dashboard",
    description="Executes all widgets in the dashboard and returns computed results.",
)
def render_dashboard(
    dashboard_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    dash = db.query(Dashboard).filter(Dashboard.id == dashboard_id, Dashboard.user_id == user.id).first()
    if not dash:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    widgets = (
        db.query(DashboardWidget)
        .filter(DashboardWidget.dashboard_id == dash.id)
        .order_by(DashboardWidget.id.asc())
        .all()
    )

    rendered = []
    for w in widgets:
        # Validate stored JSON back into the discriminated union type.
        params: WidgetParams = TypeAdapter(WidgetParams).validate_python(w.params_json)

        # Dispatch based on params.type (the discriminator)
        if params.type == "publisher_overview":
            result = publisher_overview(
                publisher_slug=params.publisher_slug,
                from_year=params.from_year,
                to_year=params.to_year,
                db=db,
            )

        elif params.type == "publisher_hit_rate":
            result = publisher_hit_rate(
                threshold=params.threshold,
                min_titles=params.min_titles,
                region=params.region,
                limit=50,
                db=db,
            )

        elif params.type == "publisher_efficiency":
            result = publisher_efficiency(
                metric=params.metric,
                min_titles=params.min_titles,
                limit=50,
                db=db,
            )

        elif params.type == "publisher_regional_bias":
            result = publisher_regional_bias(
                region=params.region,
                min_titles=params.min_titles,
                limit=50,
                db=db,
            )

        elif params.type == "publisher_momentum":
            result = publisher_momentum(
                window=params.window,
                region=params.region,
                min_titles=params.min_titles,
                limit=50,
                db=db,
            )

        elif params.type == "publisher_comparison":
            # Not implemented yet (next step after intelligence endpoints).
            # Keep renderer stable and return a clear message.
            result = {"detail": "publisher_comparison not implemented yet"}

        else:
            # Should be unreachable due to strict union validation.
            result = {"detail": f"Unknown widget type: {params.type}"}

        rendered.append(
            {
                "widget_id": w.id,
                "type": params.type,
                "params": w.params_json,
                "result": result,
            }
        )

    return {
        "dashboard": {"id": dash.id, "name": dash.name},
        "widget_count": len(rendered),
        "items": rendered,
    }