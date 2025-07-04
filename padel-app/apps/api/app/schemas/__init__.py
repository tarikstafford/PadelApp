# This file makes 'schemas' a Python package

# --- Import all schemas to make them accessible ---
from app.models.game import GameType
from app.schemas.booking_schemas import (
    Booking,
    BookingCreate,
    BookingStatus,
    BookingUpdate,
)
from app.schemas.club_schemas import (
    Club,
    ClubCreate,
    ClubCreateForAdmin,
    ClubRegistrationSchema,
    ClubUpdate,
    ClubWithCourts,
    ScheduleResponse,
)
from app.schemas.court_schemas import (
    AvailabilityResponse,
    BookingTimeSlot,
    CalendarTimeSlot,
    Court,
    CourtCreate,
    CourtUpdate,
    DailyAvailability,
)
from app.schemas.elo_adjustment_request_schemas import (
    EloAdjustmentRequest,
    EloAdjustmentRequestCreate,
)
from app.schemas.game_player_schemas import (
    GamePlayer,
    GamePlayerCreate,
    GamePlayerStatus,
    GamePlayerUpdate,
)
from app.schemas.game_invitation_schemas import (
    GameInvitationCreate,
    GameInvitationInfo,
    GameInvitationResponse,
)
from app.schemas.game_schemas import (
    Game,
    GameCreate,
    GameResponse,
    GameResult,
    GameResultRequest,
    GameUpdate,
    GameWithRatingsResponse,
    GameWithTeams,
    InvitationResponseRequest,
    UserInviteRequest,
)
from app.schemas.leaderboard_schemas import LeaderboardResponse, LeaderboardUserResponse
from app.schemas.team_schemas import Team, TeamCreate, TeamUpdate
from app.schemas.token_schemas import RefreshTokenRequest, Token, TokenData
from app.schemas.tournament_schemas import (
    BracketNode,
    TeamEligibilityCheck,
    TournamentBracket,
    TournamentCategoryCreate,
    TournamentCategoryResponse,
    TournamentCourtBookingCreate,
    TournamentCourtBookingResponse,
    TournamentCreate,
    TournamentDashboard,
    TournamentEligibilityResponse,
    TournamentListResponse,
    TournamentMatchCreate,
    TournamentMatchResponse,
    TournamentMatchUpdate,
    TournamentResponse,
    TournamentStats,
    TournamentTeamCreate,
    TournamentTeamResponse,
    TournamentTrophyResponse,
    TournamentUpdate,
)
from app.schemas.user_schemas import EloAdjustmentRequest as EloAdjustmentRequestSchema
from app.schemas.user_schemas import (
    User,
    UserCreate,
    UserInDB,
    UserLogin,
    UserSearchResult,
    UserUpdate,
    UserWithElo,
)

# --- Define what is exported when 'from app.schemas import *' is used ---
__all__ = [
    "AvailabilityResponse",
    # Booking
    "Booking",
    "BookingCreate",
    "BookingStatus",
    "BookingTimeSlot",
    "BookingUpdate",
    "BracketNode",
    "CalendarTimeSlot",
    # Club
    "Club",
    "ClubCreate",
    "ClubCreateForAdmin",
    "ClubRegistrationSchema",
    "ClubUpdate",
    "ClubWithCourts",
    # Court
    "Court",
    "CourtCreate",
    "CourtUpdate",
    "DailyAvailability",
    # ELO
    "EloAdjustmentRequest",
    "EloAdjustmentRequestCreate",
    "EloAdjustmentRequestSchema",
    # Game
    "Game",
    "GameCreate",
    # Game Invitations
    "GameInvitationCreate",
    "GameInvitationInfo", 
    "GameInvitationResponse",
    # GamePlayer
    "GamePlayer",
    "GamePlayerCreate",
    "GamePlayerStatus",
    "GamePlayerUpdate",
    "GameResponse",
    "GameResult",
    "GameResultRequest",
    "GameType",
    "GameUpdate",
    "GameWithRatingsResponse",
    "GameWithTeams",
    "InvitationResponseRequest",
    # Leaderboard
    "LeaderboardResponse",
    "LeaderboardUserResponse",
    "RefreshTokenRequest",
    "ScheduleResponse",
    # Team
    "Team",
    "TeamCreate",
    "TeamEligibilityCheck",
    "TeamUpdate",
    # Token
    "Token",
    "TokenData",
    "TournamentBracket",
    "TournamentCategoryCreate",
    "TournamentCategoryResponse",
    "TournamentCourtBookingCreate",
    "TournamentCourtBookingResponse",
    # Tournament
    "TournamentCreate",
    "TournamentDashboard",
    "TournamentEligibilityResponse",
    "TournamentListResponse",
    "TournamentMatchCreate",
    "TournamentMatchResponse",
    "TournamentMatchUpdate",
    "TournamentResponse",
    "TournamentStats",
    "TournamentTeamCreate",
    "TournamentTeamResponse",
    "TournamentTrophyResponse",
    "TournamentUpdate",
    # User
    "User",
    "UserCreate",
    "UserInDB",
    "UserInviteRequest",
    "UserLogin",
    "UserSearchResult",
    "UserUpdate",
    "UserWithElo",
]

# --- Rebuild models to resolve Pydantic forward references ---
# This is crucial for models that reference each other with string hints
ClubWithCourts.model_rebuild()
ScheduleResponse.model_rebuild()
Game.model_rebuild()
GameWithTeams.model_rebuild()
GameWithRatingsResponse.model_rebuild()
Team.model_rebuild()
