import enum
from sqlalchemy import Column, Integer, String, Boolean, Numeric, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.database import Base

class SurfaceType(str, enum.Enum):
    TURF = "turf"
    CLAY = "clay"
    HARD_COURT = "hard_court"
    SAND = "sand"

class CourtAvailabilityStatus(str, enum.Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    MAINTENANCE = "maintenance"

class Court(Base):
    __tablename__ = "courts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True) # e.g., "Court 1", "Center Court"
    club_id = Column(Integer, ForeignKey("clubs.id"), nullable=False)
    surface_type = Column(Enum(SurfaceType, values_callable=lambda obj: [e.value for e in obj]), nullable=True)
    is_indoor = Column(Boolean, default=False)
    price_per_hour = Column(Numeric(10, 2), nullable=True) # e.g., 25.00
    default_availability_status = Column(Enum(CourtAvailabilityStatus, values_callable=lambda obj: [e.value for e in obj]), default=CourtAvailabilityStatus.AVAILABLE)

    # Relationship to Club model
    club = relationship("Club", back_populates="courts")

    # Relationship to Booking model
    bookings = relationship("Booking", back_populates="court", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Court(id={self.id}, name='{self.name}', club_id={self.club_id})>" 