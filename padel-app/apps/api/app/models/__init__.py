# This file makes 'models' a Python package

# Import Base from database to make it accessible for Alembic and model definitions
from app.database import Base

# Import all model classes and enums to make them easily accessible
from .user import User, PreferredPosition
from .user_role import UserRole
from .club import Club
from .court import Court
from .booking import Booking, BookingStatus
from .game import Game, GameType
from .game_player import GamePlayer, GamePlayerStatus
from .team import Team, team_players
from .elo_adjustment_request import EloAdjustmentRequest, EloAdjustmentRequestStatus
from .club_admin import ClubAdmin
from .tournament import (
    Tournament, 
    TournamentStatus, 
    TournamentType, 
    TournamentCategory,
    TournamentCategoryConfig,
    TournamentTeam,
    TournamentMatch,
    MatchStatus,
    TournamentCourtBooking,
    TournamentTrophy,
    CATEGORY_ELO_RANGES
)

# Optional: Define __all__ to control `from app.models import *` behavior
__all__ = [
    "Base",
    "User",
    "UserRole",
    "Club",
    "Court",
    "Booking",
    "BookingStatus",
    "Game",
    "GameType",
    "GamePlayer",
    "GamePlayerStatus",
    "PreferredPosition",
    "Team",
    "team_players",
    "EloAdjustmentRequest",
    "EloAdjustmentRequestStatus",
    "ClubAdmin",
    "Tournament",
    "TournamentStatus",
    "TournamentType", 
    "TournamentCategory",
    "TournamentCategoryConfig",
    "TournamentTeam",
    "TournamentMatch",
    "MatchStatus",
    "TournamentCourtBooking",
    "TournamentTrophy",
    "CATEGORY_ELO_RANGES",
] 