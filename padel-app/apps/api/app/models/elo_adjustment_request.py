from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SAEnum, DateTime, func, Float
from sqlalchemy.orm import relationship
import enum
from app.database import Base

class EloAdjustmentRequestStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class EloAdjustmentRequest(Base):
    __tablename__ = "elo_adjustment_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    current_elo = Column(Float, nullable=False)
    requested_elo = Column(Float, nullable=False)
    reason = Column(String, nullable=True)
    
    status = Column(
        SAEnum(EloAdjustmentRequestStatus, name="eloadjustmentrequeststatus", create_enum=False),
        nullable=False,
        default=EloAdjustmentRequestStatus.PENDING,
        server_default=EloAdjustmentRequestStatus.PENDING.value
    )
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationship to User
    user = relationship("User", back_populates="elo_adjustment_requests")

    def __repr__(self):
        return f"<EloAdjustmentRequest(id={self.id}, user_id={self.user_id}, status='{self.status}')>" 