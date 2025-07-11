from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models import PreferredPosition
from app.models.user_role import UserRole  # Import the enum


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
    elo_rating: float = Field(default=1.0, ge=1.0, le=7.0)
    preferred_position: Optional[PreferredPosition] = None
    onboarding_completed: Optional[bool] = False
    onboarding_completed_at: Optional[datetime] = None
    is_game_history_public: Optional[bool] = True
    is_game_statistics_public: Optional[bool] = True

    @field_validator("role", mode="before")
    @classmethod
    def uppercase_role(cls, v):
        if isinstance(v, str):
            return v.upper()
        return v


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
    elo_rating: Optional[float] = Field(default=None, ge=1.0, le=7.0)
    preferred_position: Optional[PreferredPosition] = None
    onboarding_completed: Optional[bool] = None
    onboarding_completed_at: Optional[datetime] = None
    is_game_history_public: Optional[bool] = None
    is_game_statistics_public: Optional[bool] = None


class UserInDBBase(UserBase):
    id: int
    hashed_password: str  # This will be present for internal use / DB representation

    # Pydantic V2 way to enable ORM mode
    model_config = {"from_attributes": True}


# Schema for returning User data via API (omits hashed_password)
class User(UserBase):
    id: int
    profile_picture_url: Optional[str] = None
    is_active: Optional[bool] = None
    role: UserRole  # Add role to the main response schema
    full_name: Optional[str] = None
    elo_rating: float = Field(default=1.0, ge=1.0, le=7.0)
    preferred_position: Optional[PreferredPosition] = None
    onboarding_completed: Optional[bool] = False
    onboarding_completed_at: Optional[datetime] = None
    is_game_history_public: Optional[bool] = True
    is_game_statistics_public: Optional[bool] = True
    # model_config needed here too if this schema is created from an ORM model instance
    model_config = {"from_attributes": True}


# Schema representing a user object exactly as in the database
class UserInDB(UserInDBBase):
    pass  # Inherits all fields from UserInDBBase, including hashed_password


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserWithElo(BaseModel):
    id: int
    full_name: str
    elo_rating: float

    class Config:
        from_attributes = True


# Schema for user search results
class UserSearchResult(BaseModel):
    id: int
    full_name: str
    profile_picture_url: Optional[str] = None

    model_config = {"from_attributes": True}


class EloAdjustmentRequest(BaseModel):
    requested_rating: float = Field(..., ge=1.0, le=7.0)
    reason: str = Field(..., min_length=10, max_length=500)


class SkillAssessmentRequest(BaseModel):
    """Schema for skill assessment during onboarding"""

    years_playing: int = Field(..., ge=0, le=50, description="Years playing padel")
    playing_frequency: str = Field(
        ..., description="How often they play (e.g., 'weekly', 'monthly')"
    )
    skill_level: str = Field(..., description="Self-assessed skill level")
    preferred_position: Optional[PreferredPosition] = None
    calculated_elo: float = Field(
        ..., ge=1.0, le=7.0, description="Calculated ELO rating from assessment"
    )


class SkillAssessmentResponse(BaseModel):
    """Response after completing skill assessment"""

    success: bool
    message: str
    new_elo_rating: float
    preferred_position: Optional[PreferredPosition] = None
