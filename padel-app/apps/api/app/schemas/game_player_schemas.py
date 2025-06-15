from pydantic import BaseModel
from app.models.game_player import GamePlayerStatus
from .user_schemas import User as UserSchema

class GamePlayerBase(BaseModel):
    user_id: int
    status: GamePlayerStatus = GamePlayerStatus.INVITED

class GamePlayerCreate(GamePlayerBase):
    pass

class GamePlayerUpdate(BaseModel):
    status: GamePlayerStatus

class GamePlayer(BaseModel): # Renamed from GamePlayerResponse
    user: UserSchema
    status: GamePlayerStatus

    model_config = {"from_attributes": True} 