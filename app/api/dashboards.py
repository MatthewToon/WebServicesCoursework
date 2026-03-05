"""
Dashboards router.

Dashboards are the primary user-owned CRUD resource in the API.
Widgets are nested resources that store validated configuration JSON for
analytics endpoints (publisher intelligence, comparisons, etc).

All routes require JWT authentication.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.dashboard import Dashboard
from app.models.dashboard_widget import DashboardWidget
from app.schemas.common import PageMeta
from app.schemas.dashboard import (
    DashboardCreateIn,
    DashboardUpdateIn,
    DashboardOut,
    DashboardListOut,
    WidgetCreateIn,
    WidgetOut,
)

router = APIRouter(prefix="/dashboards", tags=["dashboards"])


@router.post("", response_model=DashboardOut, status_code=status.HTTP_201_CREATED, summary="Create a dashboard")
def create_dashboard(
    payload: DashboardCreateIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    dash = Dashboard(user_id=user.id, name=payload.name, description=payload.description)
    db.add(dash)
    db.commit()
    db.refresh(dash)
    return dash


@router.get("", response_model=DashboardListOut, summary="List my dashboards")
def list_my_dashboards(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = db.query(Dashboard).filter(Dashboard.user_id == user.id)
    total = q.count()
    items = (
        q.order_by(Dashboard.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return DashboardListOut(items=items, meta=PageMeta(page=page, page_size=page_size, total=total))


@router.get("/{dashboard_id}", response_model=DashboardOut, summary="Get a dashboard by id")
def get_dashboard(
    dashboard_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    dash = db.query(Dashboard).filter(Dashboard.id == dashboard_id, Dashboard.user_id == user.id).first()
    if not dash:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return dash


@router.patch("/{dashboard_id}", response_model=DashboardOut, summary="Update a dashboard")
def update_dashboard(
    dashboard_id: int,
    payload: DashboardUpdateIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    dash = db.query(Dashboard).filter(Dashboard.id == dashboard_id, Dashboard.user_id == user.id).first()
    if not dash:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    if payload.name is not None:
        dash.name = payload.name
    if payload.description is not None:
        dash.description = payload.description

    db.commit()
    db.refresh(dash)
    return dash


@router.delete("/{dashboard_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a dashboard")
def delete_dashboard(
    dashboard_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    dash = db.query(Dashboard).filter(Dashboard.id == dashboard_id, Dashboard.user_id == user.id).first()
    if not dash:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    db.delete(dash)
    db.commit()
    return None


# ---------------------------
# Widgets (nested resource)
# ---------------------------

@router.get("/{dashboard_id}/widgets", response_model=list[WidgetOut], summary="List widgets in a dashboard")
def list_widgets(
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
        .order_by(DashboardWidget.id)
        .all()
    )

    out: list[WidgetOut] = []
    for w in widgets:
        out.append(
            WidgetOut(
                id=w.id,
                dashboard_id=w.dashboard_id,
                params=w.params_json,  # Pydantic validates against the discriminator union
            )
        )
    return out


@router.get(
    "/{dashboard_id}/widgets/{widget_id}",
    response_model=WidgetOut,
    summary="Get a single widget from a dashboard",
)
def get_widget(
    dashboard_id: int,
    widget_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Ensure the dashboard belongs to the current user
    dash = db.query(Dashboard).filter(Dashboard.id == dashboard_id, Dashboard.user_id == user.id).first()
    if not dash:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    widget = (
        db.query(DashboardWidget)
        .filter(DashboardWidget.id == widget_id, DashboardWidget.dashboard_id == dash.id)
        .first()
    )
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")

    return WidgetOut(
        id=widget.id,
        dashboard_id=widget.dashboard_id,
        params=widget.params_json,
    )


@router.post(
    "/{dashboard_id}/widgets",
    response_model=WidgetOut,
    status_code=status.HTTP_201_CREATED,
    summary="Add a widget to a dashboard",
)
def add_widget(
    dashboard_id: int,
    payload: WidgetCreateIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    dash = db.query(Dashboard).filter(Dashboard.id == dashboard_id, Dashboard.user_id == user.id).first()
    if not dash:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    widget = DashboardWidget(
        dashboard_id=dash.id,
        type=payload.params.type,
        params_json=payload.params.model_dump(),
    )
    db.add(widget)
    db.commit()
    db.refresh(widget)

    return WidgetOut(
        id=widget.id,
        dashboard_id=widget.dashboard_id,
        params=widget.params_json,
    )


@router.patch(
    "/{dashboard_id}/widgets/{widget_id}",
    response_model=WidgetOut,
    summary="Replace a widget's configuration",
    description="Replaces the widget config (JSON) with a newly validated config. This is a full replace, not a partial patch.",
)
def replace_widget(
    dashboard_id: int,
    widget_id: int,
    payload: WidgetCreateIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Ensure the dashboard belongs to the current user
    dash = db.query(Dashboard).filter(Dashboard.id == dashboard_id, Dashboard.user_id == user.id).first()
    if not dash:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    widget = (
        db.query(DashboardWidget)
        .filter(DashboardWidget.id == widget_id, DashboardWidget.dashboard_id == dash.id)
        .first()
    )
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")

    # Full replace: update both the stored type column and the stored JSON config
    widget.type = payload.params.type
    widget.params_json = payload.params.model_dump()

    db.commit()
    db.refresh(widget)

    return WidgetOut(
        id=widget.id,
        dashboard_id=widget.dashboard_id,
        params=widget.params_json,
    )


@router.delete(
    "/{dashboard_id}/widgets/{widget_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a widget from a dashboard",
)
def delete_widget(
    dashboard_id: int,
    widget_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    dash = db.query(Dashboard).filter(Dashboard.id == dashboard_id, Dashboard.user_id == user.id).first()
    if not dash:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    widget = (
        db.query(DashboardWidget)
        .filter(DashboardWidget.id == widget_id, DashboardWidget.dashboard_id == dash.id)
        .first()
    )
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")

    db.delete(widget)
    db.commit()
    return None