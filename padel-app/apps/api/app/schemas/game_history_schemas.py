from datetime import datetime
from typing import Optional, List
from enum import Enum

from pydantic import BaseModel, Field

from app.schemas.user_schemas import UserSearchResult


class GameResultType(str, Enum):
    WIN = "WIN"
    LOSS = "LOSS"
    DRAW = "DRAW"


class GameHistoryFilterType(str, Enum):
    ALL = "ALL"
    WINS = "WINS"
    LOSSES = "LOSSES"
    DRAWS = "DRAWS"


class GameHistoryQuery(BaseModel):
    """Schema for filtering and pagination of game history"""

    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(10, ge=1, le=100, description="Maximum number of records to return")

    # Date filters
    start_date: Optional[datetime] = Field(None, description="Filter games from this date")
    end_date: Optional[datetime] = Field(None, description="Filter games until this date")

    # Result filters
    result_filter: Optional[GameHistoryFilterType] = Field(
        GameHistoryFilterType.ALL,
        description="Filter by game result"
    )

    # Partner/opponent filters
    partner_id: Optional[int] = Field(None, description="Filter by partner user ID")
    opponent_id: Optional[int] = Field(None, description="Filter by opponent user ID")

    # Club filter
    club_id: Optional[int] = Field(None, description="Filter by club ID")

    # Include completed games only
    completed_only: bool = Field(True, description="Only include completed games")


class GameHistoryPlayer(BaseModel):
    """Player information in game history"""

    id: int
    full_name: str
    profile_picture_url: Optional[str] = None
    elo_rating: float
    position: Optional[str] = None
    team_side: Optional[str] = None

    model_config = {"from_attributes": True}


class GameHistoryTeam(BaseModel):
    """Team information in game history"""

    players: List[GameHistoryPlayer] = []
    is_winning_team: bool = False

    model_config = {"from_attributes": True}


class GameHistoryClub(BaseModel):
    """Club information in game history"""

    id: int
    name: str
    city: Optional[str] = None

    model_config = {"from_attributes": True}


class GameHistoryEntry(BaseModel):
    """Individual game history entry"""

    id: int
    game_id: int

    # Game details
    start_time: datetime
    end_time: datetime
    club: GameHistoryClub

    # Teams and players
    team1: GameHistoryTeam
    team2: GameHistoryTeam

    # Result from current user's perspective
    result: GameResultType
    user_team_side: str  # TEAM_1 or TEAM_2

    # Game score (if available)
    score: Optional[str] = None

    # ELO changes
    elo_change: Optional[float] = None
    elo_before: Optional[float] = None
    elo_after: Optional[float] = None

    # Partners and opponents for the current user
    partners: List[GameHistoryPlayer] = []
    opponents: List[GameHistoryPlayer] = []

    model_config = {"from_attributes": True}


class GameHistoryResponse(BaseModel):
    """Response schema for game history"""

    games: List[GameHistoryEntry] = []
    total_count: int
    has_more: bool

    model_config = {"from_attributes": True}


class GameStatistics(BaseModel):
    """Game statistics for a user"""

    total_games: int = 0
    wins: int = 0
    losses: int = 0
    draws: int = 0

    # Win rate
    win_rate: float = 0.0

    # ELO progression
    current_elo: float
    highest_elo: float
    lowest_elo: float
    elo_change_total: float = 0.0

    # Partner statistics
    favorite_partners: List[UserSearchResult] = []

    # Recent form (last 10 games)
    recent_form: List[GameResultType] = []

    model_config = {"from_attributes": True}


class EloProgressionPoint(BaseModel):
    """Single point in ELO progression"""

    game_id: int
    date: datetime
    elo_rating: float
    elo_change: float
    opponent_average_elo: float
    result: GameResultType

    model_config = {"from_attributes": True}


class EloProgressionResponse(BaseModel):
    """ELO progression over time"""

    progression: List[EloProgressionPoint] = []

    model_config = {"from_attributes": True}


class PartnerStatistics(BaseModel):
    """Statistics with a specific partner"""

    partner: UserSearchResult
    games_together: int
    wins_together: int
    losses_together: int
    draws_together: int
    win_rate_together: float

    model_config = {"from_attributes": True}


class ProfileGameHistoryResponse(BaseModel):
    """Public game history response for user profiles"""

    # Basic statistics (always visible)
    total_games: int = 0
    wins: int = 0
    losses: int = 0
    win_rate: float = 0.0
    current_elo: float

    # Detailed history (only if privacy allows)
    recent_games: Optional[List[GameHistoryEntry]] = None
    favorite_partners: Optional[List[UserSearchResult]] = None

    # Privacy settings
    is_history_public: bool = True
    is_statistics_public: bool = True

    model_config = {"from_attributes": True}
