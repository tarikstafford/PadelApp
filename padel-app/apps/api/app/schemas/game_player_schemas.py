from pydantic import BaseModel
from typing import Optional

from app.models.game_player import GamePlayerStatus, GamePlayerPosition, GamePlayerTeamSide
from app.schemas.user_schemas import User as UserSchema


class GamePlayerBase(BaseModel):
    user_id: int
    status: GamePlayerStatus = GamePlayerStatus.INVITED
    position: Optional[GamePlayerPosition] = None
    team_side: Optional[GamePlayerTeamSide] = None


class GamePlayerCreate(GamePlayerBase):
    pass


class GamePlayerUpdate(BaseModel):
    status: GamePlayerStatus


class GamePlayer(BaseModel):  # Renamed from GamePlayerResponse
    user: UserSchema
    status: GamePlayerStatus
    position: Optional[GamePlayerPosition] = None
    team_side: Optional[GamePlayerTeamSide] = None

    model_config = {"from_attributes": True}


class GamePlayerPositionUpdate(BaseModel):
    position: GamePlayerPosition
    team_side: GamePlayerTeamSide


class GamePlayerWithPosition(BaseModel):
    user: UserSchema
    status: GamePlayerStatus
    position: Optional[GamePlayerPosition] = None
    team_side: Optional[GamePlayerTeamSide] = None

    model_config = {"from_attributes": True}
