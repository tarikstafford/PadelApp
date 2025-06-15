from typing import Optional, List
from pydantic import BaseModel
from decimal import Decimal
from app.models.court import SurfaceType, CourtAvailabilityStatus
from datetime import datetime, date
from .user_schemas import User
from app.models import BookingStatus
# No longer import Club directly to prevent circular dependency
# from .club_schemas import Club

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
    club: "Club" # Use a forward reference (string) to avoid circular import

    model_config = {"from_attributes": True}

# --- TimeSlot Schemas for Availability ---
class BookingTimeSlot(BaseModel):
    start_time: str
    end_time: str
    is_available: bool

class CalendarTimeSlot(BaseModel):
    time: str
    booked: bool

class DailyAvailability(BaseModel):
    date: date
    slots: List[CalendarTimeSlot]

class AvailabilityResponse(BaseModel):
    days: List[DailyAvailability]

class CourtWithBookings(Court):
    # Add any additional properties specific to CourtWithBookings
    pass

# Forward reference resolution
from .club_schemas import Club
Court.model_rebuild() 