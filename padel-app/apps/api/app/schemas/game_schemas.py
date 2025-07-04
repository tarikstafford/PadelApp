from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.game import GameStatus, GameType
from app.models.game_player import GamePlayerStatus
from app.schemas.booking_schemas import BookingWithCourt
from app.schemas.game_player_schemas import GamePlayer
from app.schemas.team_schemas import Team
from app.schemas.user_schemas import User as UserSchema


# --- Team Schemas (for game context) ---
class TeamWithPlayers(Team):
    # Inherits from team_schemas.Team which has id, name, and players list.
    pass


# --- Game Schemas ---
class GameBase(BaseModel):
    game_type: Optional[GameType] = GameType.PRIVATE
    skill_level: Optional[str] = None


class GameCreate(GameBase):
    booking_id: int


class GameUpdate(BaseModel):
    game_type: Optional[GameType] = None
    skill_level: Optional[str] = None


class Game(GameBase):
    id: int
    club_id: int
    start_time: datetime
    end_time: datetime
    booking_id: int
    game_status: Optional[GameStatus] = GameStatus.SCHEDULED
    players: list[GamePlayer] = []
    booking: BookingWithCourt

    model_config = {"from_attributes": True}


class GameResponse(Game):
    pass


class GameWithTeams(Game):
    teams: list[TeamWithPlayers] = []


class GameInDB(Game):
    pass


# --- Game Result Schemas ---
class GameResult(BaseModel):
    game_id: int
    winning_team_id: Optional[int] = None
    score: Optional[str] = None


class GameResultRequest(BaseModel):
    winning_team_id: int


class UserWithRating(UserSchema):
    elo_rating: float


class GameWithRatingsResponse(Game):
    players: list[UserWithRating] = []


# --- Invitation Schema ---
class UserInviteRequest(BaseModel):
    user_id_to_invite: int


class InvitationResponseRequest(BaseModel):
    status: GamePlayerStatus  # User will send "accepted" or "declined"
