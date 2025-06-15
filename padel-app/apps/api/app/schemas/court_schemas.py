from typing import Optional, List
from pydantic import BaseModel
from decimal import Decimal
from app.models.court import SurfaceType, CourtAvailabilityStatus
from datetime import datetime, date

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
    id: int
    club_id: int
    club: "Club" # Use string literal for forward reference

    model_config = {"from_attributes": True}

# --- TimeSlot Schema for Availability ---
class TimeSlot(BaseModel):
    start_time: datetime
    end_time: datetime
    is_available: bool

class DailyAvailability(BaseModel):
    date: date
    slots: List[TimeSlot]

class AvailabilityResponse(BaseModel):
    availability: List[DailyAvailability]


# Forward reference resolution
from .club_schemas import Club
Court.model_rebuild() 