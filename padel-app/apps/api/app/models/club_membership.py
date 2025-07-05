"""Club membership model."""

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class ClubMembership(Base):
    """Club membership model."""

    __tablename__ = "club_memberships"

    id = Column(Integer, primary_key=True, index=True)
    club_id = Column(Integer, ForeignKey("clubs.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    membership_type = Column(
        String(50), nullable=False
    )  # monthly, yearly, premium, etc.
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    monthly_fee = Column(Numeric(10, 2), nullable=True)
    is_active = Column(Boolean, nullable=False, server_default="true")
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relationships
    club = relationship("Club", back_populates="memberships")
    user = relationship("User", back_populates="club_memberships")
