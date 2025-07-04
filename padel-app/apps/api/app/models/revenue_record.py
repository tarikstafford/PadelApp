"""Revenue record model."""

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class RevenueRecord(Base):
    """Revenue record model."""

    __tablename__ = "revenue_records"

    id = Column(Integer, primary_key=True, index=True)
    club_id = Column(Integer, ForeignKey("clubs.id"), nullable=False)
    revenue_type = Column(String(50), nullable=False)  # booking, tournament, membership, other
    source_id = Column(Integer, nullable=True)  # Reference to booking_id, tournament_id, etc.
    amount = Column(Numeric(10, 2), nullable=False)
    date = Column(Date, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relationships
    club = relationship("Club", back_populates="revenue_records")
