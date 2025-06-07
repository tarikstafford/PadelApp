from typing import Optional, List
from pydantic import BaseModel
from decimal import Decimal # For price_per_hour

# Shared properties
class CourtBase(BaseModel):
    name: str
    surface_type: Optional[str] = None
    is_indoor: Optional[bool] = False
    price_per_hour: Optional[Decimal] = None
    default_availability_status: Optional[str] = "Available"

# Properties to receive on court creation
class CourtCreate(CourtBase):
    club_id: int # Must be specified on creation

class CourtCreateForAdmin(CourtBase):
    pass # club_id will be derived from the authenticated admin's club

# Properties to receive on court update
class CourtUpdate(CourtBase):
    name: Optional[str] = None # All fields optional for update
    club_id: Optional[int] = None
    # Other fields inherit optionality from CourtBase

# Properties stored in DB
class CourtInDBBase(CourtBase):
    id: int
    club_id: int
    model_config = {"from_attributes": True}

# Properties to return to client
class Court(CourtInDBBase):
    pass # Inherits all from CourtInDBBase

# Properties stored in DB
class CourtInDB(CourtInDBBase):
    pass 