from typing import Optional, List
from pydantic import BaseModel, EmailStr, validator, HttpUrl
from datetime import time

from .user_schemas import User as UserSchema # Import for nesting owner details

# No longer import Court directly to prevent circular dependency
# from .court_schemas import Court

# Forward declaration for CourtBase to be used in Club schema
class CourtBase(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}

# Shared properties
class ClubBase(BaseModel):
    name: str
    description: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    opening_time: Optional[time] = None
    closing_time: Optional[time] = None
    opening_hours_display: Optional[str] = None
    amenities: Optional[str] = None
    image_url: Optional[str] = None # Allow string for now, HttpUrl is too strict for data entry

    @validator("email", "image_url", pre=True)
    def empty_str_to_none(cls, v):
        if v == "" or v is None:
            return None
        return v

# Properties for club and admin registration
class ClubRegistrationSchema(ClubBase):
    admin_email: EmailStr
    admin_name: Optional[str] = None
    admin_password: str

# Properties to receive on club creation via a direct call (e.g., by a superuser)
class ClubCreate(ClubBase):
    owner_id: int

# Properties to receive on club creation via the admin route, where owner_id is derived
class ClubCreateForAdmin(ClubBase):
    name: str # Make sure name is explicitly required

# Properties to receive on club update
class ClubUpdate(ClubBase):
    name: Optional[str] = None # All fields optional for update
    # Other fields inherit optionality from ClubBase

# Properties stored in DB
class ClubInDBBase(ClubBase):
    id: int
    owner_id: int
    owner: Optional[UserSchema] = None # Include owner details in the response
    model_config = {"from_attributes": True}

# Properties to return to client (basic club info)
class Club(ClubInDBBase):
    courts: List[CourtBase] = [] # Use the simplified CourtBase to break the cycle
    
    class Config:
        model_config = {"from_attributes": True}

# Properties to return to client (club info with its courts)
class ClubWithCourts(Club):
    pass

# Properties stored in DB
class ClubInDB(ClubInDBBase):
    pass 

class ScheduleResponse(BaseModel):
    courts: List["Court"]
    bookings: List["Booking"]

    model_config = {"from_attributes": True}

# A slimmed-down version for lists where full details are not needed.
class ClubBasicInfo(BaseModel):
    id: int
    name: str
    city: Optional[str] = None
    image_url: Optional[HttpUrl] = None

    model_config = {"from_attributes": True}

# Forward reference resolution
from .court_schemas import Court
from .booking_schemas import Booking
Club.model_rebuild()
ScheduleResponse.model_rebuild() 