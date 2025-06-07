from typing import Optional, List
from pydantic import BaseModel, EmailStr

from .court_schemas import Court # Import Court schema for use in ClubWithCourts
from .user_schemas import User as UserSchema # Import for nesting owner details

# Shared properties
class ClubBase(BaseModel):
    name: str
    address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    description: Optional[str] = None # Changed from Text in model to str for Pydantic
    opening_hours: Optional[str] = None
    amenities: Optional[str] = None
    image_url: Optional[str] = None

# Properties for club and admin registration
class ClubRegistrationSchema(ClubBase):
    admin_email: EmailStr
    admin_name: Optional[str] = None
    admin_password: str

# Properties to receive on club creation
class ClubCreate(ClubBase):
    pass # All fields from ClubBase are needed/optional as defined there

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
    pass # Inherits all from ClubInDBBase

# Properties to return to client (club info with its courts)
class ClubWithCourts(Club):
    courts: List[Court] = []

# Properties stored in DB
class ClubInDB(ClubInDBBase):
    pass 