"""Club daily analytics model."""

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class ClubDailyAnalytics(Base):
    """Club daily analytics model."""

    __tablename__ = "club_daily_analytics"

    id = Column(Integer, primary_key=True, index=True)
    club_id = Column(Integer, ForeignKey("clubs.id"), nullable=False)
    date = Column(Date, nullable=False)
    total_bookings = Column(Integer, nullable=False, server_default="0")
    total_revenue = Column(Numeric(10, 2), nullable=False, server_default="0")
    unique_players = Column(Integer, nullable=False, server_default="0")
    court_utilization_rate = Column(Numeric(5, 2), nullable=True)
    average_booking_duration = Column(Numeric(5, 2), nullable=True)
    peak_hour = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relationships
    club = relationship("Club", back_populates="daily_analytics")

    # Constraints
    __table_args__ = (UniqueConstraint("club_id", "date"),)
