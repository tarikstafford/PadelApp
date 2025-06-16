from pydantic import BaseModel, Field
from datetime import datetime

class EloAdjustmentRequestBase(BaseModel):
    requested_rating: float = Field(..., ge=1.0, le=7.0)
    reason: str = Field(..., min_length=10, max_length=500)

class EloAdjustmentRequestCreate(EloAdjustmentRequestBase):
    pass

class EloAdjustmentRequest(EloAdjustmentRequestBase):
    id: int
    user_id: int
    status: str
    created_at: datetime
    current_elo: float
    requested_elo: float

    class Config:
        from_attributes = True 