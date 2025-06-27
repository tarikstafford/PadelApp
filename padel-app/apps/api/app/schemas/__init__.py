# This file makes 'schemas' a Python package

# --- Import all schemas to make them accessible ---
from .user_schemas import User, UserCreate, UserUpdate, UserInDB, UserLogin, UserWithElo, EloAdjustmentRequest as EloAdjustmentRequestSchema, UserSearchResult
from .token_schemas import Token, TokenData, RefreshTokenRequest
from .club_schemas import Club, ClubCreate, ClubUpdate, ClubWithCourts, ClubRegistrationSchema, ClubCreateForAdmin, ScheduleResponse
from .court_schemas import Court, CourtCreate, CourtUpdate, BookingTimeSlot, CalendarTimeSlot, DailyAvailability, AvailabilityResponse
from .booking_schemas import Booking, BookingCreate, BookingUpdate, BookingStatus
from .game_schemas import (
    Game, GameCreate, GameUpdate, GameResponse, GameWithTeams,
    GameResult, GameResultRequest, GameWithRatingsResponse,
    UserInviteRequest, InvitationResponseRequest
)
from .game_player_schemas import GamePlayer, GamePlayerCreate, GamePlayerUpdate, GamePlayerStatus
from .team_schemas import Team, TeamCreate, TeamUpdate
from .leaderboard_schemas import LeaderboardResponse, LeaderboardUserResponse
from .elo_adjustment_request_schemas import EloAdjustmentRequest, EloAdjustmentRequestCreate
from .tournament_schemas import (
    TournamentCreate, TournamentUpdate, TournamentResponse, TournamentListResponse,
    TournamentCategoryCreate, TournamentCategoryResponse,
    TournamentTeamCreate, TournamentTeamResponse,
    TournamentMatchCreate, TournamentMatchUpdate, TournamentMatchResponse,
    TournamentBracket, BracketNode,
    TournamentCourtBookingCreate, TournamentCourtBookingResponse,
    TournamentTrophyResponse,
    TeamEligibilityCheck, TournamentEligibilityResponse,
    TournamentStats, TournamentDashboard
)
from app.models.game import GameType


# --- Define what is exported when 'from app.schemas import *' is used ---
__all__ = [
    # User
    "User",
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    "UserLogin",
    "UserWithElo",
    "UserSearchResult",
    "EloAdjustmentRequestSchema",
    # Token
    "Token",
    "TokenData",
    "RefreshTokenRequest",
    # Club
    "Club",
    "ClubCreate",
    "ClubUpdate",
    "ClubWithCourts",
    "ClubRegistrationSchema",
    "ClubCreateForAdmin",
    "ScheduleResponse",
    # Court
    "Court",
    "CourtCreate",
    "CourtUpdate",
    "BookingTimeSlot",
    "CalendarTimeSlot",
    "DailyAvailability",
    "AvailabilityResponse",
    # Booking
    "Booking",
    "BookingCreate",
    "BookingUpdate",
    "BookingStatus",
    # Game
    "Game",
    "GameCreate",
    "GameUpdate",
    "GameResponse",
    "GameWithTeams",
    "GameResult",
    "GameResultRequest",
    "GameWithRatingsResponse",
    "UserInviteRequest",
    "InvitationResponseRequest",
    "GameType",
    # GamePlayer
    "GamePlayer",
    "GamePlayerCreate",
    "GamePlayerUpdate",
    "GamePlayerStatus",
    # Team
    "Team",
    "TeamCreate",
    "TeamUpdate",
    # Leaderboard
    "LeaderboardResponse",
    "LeaderboardUserResponse",
    # ELO
    "EloAdjustmentRequest",
    "EloAdjustmentRequestCreate",
    # Tournament
    "TournamentCreate",
    "TournamentUpdate", 
    "TournamentResponse",
    "TournamentListResponse",
    "TournamentCategoryCreate",
    "TournamentCategoryResponse",
    "TournamentTeamCreate",
    "TournamentTeamResponse",
    "TournamentMatchCreate",
    "TournamentMatchUpdate",
    "TournamentMatchResponse",
    "TournamentBracket",
    "BracketNode",
    "TournamentCourtBookingCreate",
    "TournamentCourtBookingResponse",
    "TournamentTrophyResponse",
    "TeamEligibilityCheck",
    "TournamentEligibilityResponse",
    "TournamentStats",
    "TournamentDashboard",
]

# --- Rebuild models to resolve Pydantic forward references ---
# This is crucial for models that reference each other with string hints
ClubWithCourts.model_rebuild()
ScheduleResponse.model_rebuild()
Game.model_rebuild()
GameWithTeams.model_rebuild()
GameWithRatingsResponse.model_rebuild()
Team.model_rebuild() 