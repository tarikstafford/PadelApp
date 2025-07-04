from datetime import datetime

# Forward reference for Game schema
from typing import TYPE_CHECKING, Optional

from pydantic import BaseModel

if TYPE_CHECKING:
    from app.schemas.game_schemas import Game as GameSchema

# Import BookingStatus enum from the ORM model
# This assumes no circular dependency issues. If there are,
# the enum might need to be defined in a common types module or duplicated.
from app.models.booking import BookingStatus
from app.schemas.court_schemas import Court, CourtWithClub
from app.schemas.user_schemas import User


# Shared properties for a booking
class BookingBase(BaseModel):
    court_id: int
    start_time: datetime  # Frontend will send this, backend will calculate end_time


# Properties to receive on booking creation
# user_id will be taken from the authenticated user in the endpoint
class BookingCreate(BookingBase):
    duration: int  # Duration in minutes, e.g., 60 or 90


class BookingUpdate(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[BookingStatus] = None


# Properties to return to client
class Booking(BookingBase):
    id: int
    user_id: int
    end_time: datetime
    status: BookingStatus  # Use the enum from the model
    user: User
    court: Court
    game: Optional["GameSchema"] = None

    model_config = {"from_attributes": True}


# For more detailed DB representation if needed (can often be same as Booking)
class BookingInDB(Booking):
    pass


class BookingWithCourt(BookingBase):
    id: int
    end_time: datetime
    court: CourtWithClub
    model_config = {"from_attributes": True}


# --- Fix for Pydantic forward reference ---
from app.schemas.game_schemas import Game as GameSchema

Booking.model_rebuild()
