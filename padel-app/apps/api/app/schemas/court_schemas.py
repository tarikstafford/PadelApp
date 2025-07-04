from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel

from app.models.court import CourtAvailabilityStatus, SurfaceType

# No longer import Club directly to prevent circular dependency
# from .club_schemas import Club


# Forward declaration for a simplified Club schema
class ClubBase(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


# Shared properties
class CourtBase(BaseModel):
    name: str
    surface_type: Optional[SurfaceType] = None
    is_indoor: Optional[bool] = False
    price_per_hour: Optional[Decimal] = None
    default_availability_status: Optional[
        CourtAvailabilityStatus
    ] = CourtAvailabilityStatus.AVAILABLE


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
    club: ClubBase  # Use the simplified ClubBase to break the cycle

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
    slots: list[CalendarTimeSlot]


class AvailabilityResponse(BaseModel):
    days: list[DailyAvailability]


class CourtWithBookings(Court):
    # Add any additional properties specific to CourtWithBookings
    pass


class CourtWithClub(CourtBase):
    id: int
    club: ClubBase
    model_config = {"from_attributes": True}
