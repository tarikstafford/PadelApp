from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database import Base

class EloAdjustmentRequestStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class EloAdjustmentRequest(Base):
    __tablename__ = "elo_adjustment_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    current_rating = Column(Float, nullable=False)
    requested_rating = Column(Float, nullable=False)
    reason = Column(String, nullable=False)
    status = Column(Enum(EloAdjustmentRequestStatus), default=EloAdjustmentRequestStatus.PENDING, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="elo_adjustment_requests") 