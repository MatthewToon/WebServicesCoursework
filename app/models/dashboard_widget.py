"""
DashboardWidget model.

Represents a single widget within a dashboard.
Each widget references an analytics endpoint and stores
its configuration parameters as JSON.
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.db import Base


class DashboardWidget(Base):
    __tablename__ = "dashboard_widgets"

    id = Column(Integer, primary_key=True, index=True)

    dashboard_id = Column(Integer, ForeignKey("dashboards.id"), nullable=False)

    type = Column(String(80), nullable=False)

    params_json = Column(JSONB, nullable=False)

    dashboard = relationship("Dashboard", back_populates="widgets")