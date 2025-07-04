"""Payment transaction model."""

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class PaymentTransaction(Base):
    """Payment transaction model."""

    __tablename__ = "payment_transactions"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    club_id = Column(Integer, ForeignKey("clubs.id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False, server_default="EUR")
    payment_method = Column(String(50), nullable=True)
    payment_status = Column(String(20), nullable=False)  # pending, completed, failed, refunded
    payment_gateway = Column(String(50), nullable=True)
    gateway_transaction_id = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)
    payment_metadata = Column(JSON, nullable=True)

    # Relationships
    booking = relationship("Booking", back_populates="payment_transactions")
    tournament = relationship("Tournament", back_populates="payment_transactions")
    user = relationship("User", back_populates="payment_transactions")
    club = relationship("Club", back_populates="payment_transactions")