# This file makes 'schemas' a Python package

from .user_schemas import User, UserBase, UserCreate, UserUpdate, UserInDB, UserSearchResult
from .token_schemas import Token, TokenPayload, RefreshTokenRequest
from .club_schemas import Club, ClubCreate, ClubUpdate, ClubWithCourts, ClubRegistrationSchema
from .court_schemas import Court, CourtCreate, CourtUpdate, CourtCreateForAdmin, CourtAvailabilityResponse
from .availability_schemas import TimeSlot
from .booking_schemas import Booking, BookingCreate
from .game_schemas import GameCreate, GameResponse, GamePlayerResponse, UserInviteRequest, InvitationResponseRequest

# Resolve forward references
Booking.model_rebuild()
GameResponse.model_rebuild()

__all__ = [
    "User",
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    "UserSearchResult",
    "Token",
    "TokenPayload",
    "RefreshTokenRequest",
    "Club",
    "ClubCreate",
    "ClubUpdate",
    "ClubWithCourts",
    "ClubRegistrationSchema",
    "Court",
    "CourtCreate",
    "CourtUpdate",
    "CourtCreateForAdmin",
    "CourtAvailabilityResponse",
    "TimeSlot",
    "Booking",
    "BookingCreate",
    "GameCreate",
    "GameResponse",
    "GamePlayerResponse",
    "UserInviteRequest",
    "InvitationResponseRequest",
] 