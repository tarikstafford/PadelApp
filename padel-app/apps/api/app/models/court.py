from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Numeric
from sqlalchemy.orm import relationship

from app.database import Base

class Court(Base):
    __tablename__ = "courts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False) # e.g., "Court 1", "Center Court"
    club_id = Column(Integer, ForeignKey("clubs.id"), nullable=False)
    surface_type = Column(String, nullable=True) # e.g., "Artificial Grass", "Concrete"
    is_indoor = Column(Boolean, default=False)
    price_per_hour = Column(Numeric(10, 2), nullable=True) # e.g., 25.00
    default_availability_status = Column(String, nullable=True, default="Available") # e.g., "Available", "Maintenance"

    # Relationship to Club model
    club = relationship("Club", back_populates="courts")

    # Relationship to Booking model
    bookings = relationship("Booking", back_populates="court", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Court(id={self.id}, name='{self.name}', club_id={self.club_id})>" 