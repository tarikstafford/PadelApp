import enum
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from app.database import Base


# Enum for booking status
class BookingStatus(str, enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    court_id = Column(Integer, ForeignKey("courts.id"), nullable=False)
    user_id = Column(
        Integer, ForeignKey("users.id"), nullable=False
    )  # User who made the booking
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(
        SAEnum(BookingStatus), default=BookingStatus.PENDING, nullable=False
    )

    # Relationship to Court model
    court = relationship("Court", back_populates="bookings")

    # Relationship to User model (user who made the booking)
    user = relationship(
        "User"  # , back_populates="bookings"
        # Add back_populates="bookings" to User model later
    )

    # Relationship to Game model (one-to-one with Booking)
    game = relationship(
        "Game",
        uselist=False,
        back_populates="booking",
        cascade="all, delete-orphan"
    )

    @property
    def game_id(self) -> Optional[int]:
        return self.game.id if self.game else None

    def __repr__(self):
        return (
            f"<Booking(id={self.id}, court_id={self.court_id}, "
            f"user_id={self.user_id}, start_time='{self.start_time}')>"
        )
