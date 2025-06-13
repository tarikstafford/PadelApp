from typing import Optional
from pydantic import BaseModel, EmailStr
from app.models.user_role import UserRole # Import the enum

# Schema for creating a club admin
class AdminUserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str

# Shared properties
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    profile_picture_url: Optional[str] = None
    is_active: Optional[bool] = True
    role: Optional[UserRole] = UserRole.PLAYER

# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str

# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    profile_picture_url: Optional[str] = None
    is_active: Optional[bool] = None

class UserInDBBase(UserBase):
    id: int
    hashed_password: str # This will be present for internal use / DB representation

    # Pydantic V2 way to enable ORM mode
    model_config = {"from_attributes": True}

# Schema for returning User data via API (omits hashed_password)
class User(UserBase):
    id: int
    profile_picture_url: Optional[str] = None
    is_active: Optional[bool] = None
    role: UserRole # Add role to the main response schema
    full_name: Optional[str] = None
    # model_config needed here too if this schema is created from an ORM model instance
    model_config = {"from_attributes": True}

# Schema representing a user object exactly as in the database
class UserInDB(UserInDBBase):
    pass # Inherits all fields from UserInDBBase, including hashed_password

# Schema for user search results
class UserSearchResult(BaseModel):
    id: int
    full_name: str
    profile_picture_url: Optional[str] = None

    model_config = {"from_attributes": True} 