"""
Dashboard model.

Allows users to create saved analytical dashboards composed
of widgets that reference analytics endpoints.
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base


class Dashboard(Base):
    __tablename__ = "dashboards"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    name = Column(String(120), nullable=False)
    description = Column(Text, nullable=True)

    widgets = relationship(
        "DashboardWidget",
        cascade="all, delete-orphan",
        back_populates="dashboard"
    )