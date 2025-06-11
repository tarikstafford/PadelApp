from typing import Optional, List
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime # Though not directly in these schemas, good for context

# Import enums from models if they are to be used directly in schemas
from app.models.game import GameType
from app.models.game_player import GamePlayerStatus
from .user_schemas import User as UserSchema # For embedding user details in GamePlayerResponse
from .booking_schemas import Booking as BookingSchema # Import Booking schema

# --- GamePlayer Schemas ---
class GamePlayerBase(BaseModel):
    user_id: int
    status: GamePlayerStatus = GamePlayerStatus.INVITED # Default status

class GamePlayerCreate(GamePlayerBase):
    # Typically used internally or by specific invite endpoints
    pass

class GamePlayerResponse(BaseModel):
    user: UserSchema # Nested user details
    status: GamePlayerStatus

    model_config = {"from_attributes": True}

# --- Game Schemas ---
class GameBase(BaseModel):
    # booking_id: int # booking_id is part of the Game model, but GameResponse will have full Booking object
    game_type: Optional[GameType] = GameType.PRIVATE
    skill_level: Optional[str] = None

class GameCreate(GameBase):
    booking_id: int
    
    @validator("game_type", pre=True, always=True)
    def set_game_type_lowercase(cls, v):
        if v:
            return v.lower()
        return GameType.PRIVATE.lower()
    

class GameResponse(GameBase):
    id: int
    booking: BookingSchema # Nested booking details
    players: List[GamePlayerResponse] = [] # List of players in the game
    # booking: Optional[BookingSchema] # Could add if booking details are needed here too

    model_config = {"from_attributes": True}

# If needed for DB representation, often similar to GameResponse or includes more internal fields
class GameInDB(GameResponse):
    # Example: Might include internal fields not sent to client
    pass

# --- Invitation Schema ---
class UserInviteRequest(BaseModel):
    user_id_to_invite: int

class InvitationResponseRequest(BaseModel):
    status: GamePlayerStatus # User will send "accepted" or "declined" 