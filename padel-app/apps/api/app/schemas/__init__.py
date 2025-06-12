# This file makes 'schemas' a Python package

from .user_schemas import User, UserBase, UserCreate, UserUpdate, UserInDB, UserSearchResult
from .token_schemas import Token, TokenPayload, RefreshTokenRequest
from .club_schemas import Club, ClubCreate, ClubUpdate, ClubWithCourts, ClubRegistrationSchema
from .court_schemas import Court, CourtCreate, CourtUpdate, CourtCreateForAdmin
from .availability_schemas import TimeSlot
from .booking_schemas import Booking, BookingCreate
from .game_schemas import GameCreate, GameResponse, GamePlayerResponse, UserInviteRequest, InvitationResponseRequest

# Manually update forward references for models that have them.
# This is needed because Booking schema refers to GameResponse ('GameSchema')
# which is defined in another file.
Booking.model_rebuild()

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
    "TimeSlot",
    "Booking",
    "BookingCreate",
    "GameCreate",
    "GameResponse",
    "GamePlayerResponse",
    "UserInviteRequest",
    "InvitationResponseRequest",
] 