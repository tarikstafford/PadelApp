# This file makes 'models' a Python package

# Import Base from database to make it accessible for Alembic and model definitions
from app.database import Base
from app.models.booking import Booking, BookingStatus
from app.models.club import Club
from app.models.club_admin import ClubAdmin
from app.models.court import Court
from app.models.elo_adjustment_request import (
    EloAdjustmentRequest,
    EloAdjustmentRequestStatus,
)
from app.models.game import Game, GameType
from app.models.game_player import GamePlayer, GamePlayerStatus
from app.models.team import Team, team_players
from app.models.tournament import (
    CATEGORY_ELO_RANGES,
    MatchStatus,
    Tournament,
    TournamentCategory,
    TournamentCategoryConfig,
    TournamentCourtBooking,
    TournamentMatch,
    TournamentStatus,
    TournamentTeam,
    TournamentTrophy,
    TournamentType,
)

# Import all model classes and enums to make them easily accessible
from app.models.user import PreferredPosition, User
from app.models.user_role import UserRole

# Import new financial and analytics models
from app.models.payment_transaction import PaymentTransaction
from app.models.revenue_record import RevenueRecord
from app.models.club_daily_analytics import ClubDailyAnalytics
from app.models.club_membership import ClubMembership

# Optional: Define __all__ to control `from app.models import *` behavior
__all__ = [
    "CATEGORY_ELO_RANGES",
    "Base",
    "Booking",
    "BookingStatus",
    "Club",
    "ClubAdmin",
    "ClubDailyAnalytics",
    "ClubMembership",
    "Court",
    "EloAdjustmentRequest",
    "EloAdjustmentRequestStatus",
    "Game",
    "GamePlayer",
    "GamePlayerStatus",
    "GameType",
    "MatchStatus",
    "PaymentTransaction",
    "PreferredPosition",
    "RevenueRecord",
    "Team",
    "Tournament",
    "TournamentCategory",
    "TournamentCategoryConfig",
    "TournamentCourtBooking",
    "TournamentMatch",
    "TournamentStatus",
    "TournamentTeam",
    "TournamentTrophy",
    "TournamentType",
    "User",
    "UserRole",
    "team_players",
]
