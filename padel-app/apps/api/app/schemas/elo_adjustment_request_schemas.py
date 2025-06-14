from pydantic import BaseModel
from datetime import datetime

class EloAdjustmentRequestBase(BaseModel):
    requested_rating: float
    reason: str

class EloAdjustmentRequestCreate(EloAdjustmentRequestBase):
    pass

class EloAdjustmentRequest(EloAdjustmentRequestBase):
    id: int
    user_id: int
    status: str
    created_at: datetime

    class Config:
        orm_mode = True 