from typing import Optional, List
from pydantic import BaseModel
from decimal import Decimal
from app.models.court import SurfaceType, CourtAvailabilityStatus

# Shared properties
class CourtBase(BaseModel):
    name: str
    surface_type: Optional[SurfaceType] = None
    is_indoor: Optional[bool] = False
    price_per_hour: Optional[Decimal] = None
    default_availability_status: Optional[CourtAvailabilityStatus] = CourtAvailabilityStatus.AVAILABLE

# Properties to receive on court creation
class CourtCreate(CourtBase):
    club_id: int

class CourtCreateForAdmin(CourtBase):
    pass

# Properties to receive on court update
class CourtUpdate(CourtBase):
    name: Optional[str] = None
    club_id: Optional[int] = None

# Properties stored in DB
class CourtInDBBase(CourtBase):
    id: int
    club_id: int
    model_config = {"from_attributes": True}

# Properties to return to client
class Court(CourtInDBBase):
    pass

# Properties stored in DB
class CourtInDB(CourtInDBBase):
    pass 