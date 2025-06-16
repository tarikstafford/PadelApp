from typing import List, Optional
from pydantic import BaseModel
from .user_schemas import User

class TeamBase(BaseModel):
    name: str

class TeamCreate(TeamBase):
    pass

class TeamUpdate(TeamBase):
    name: Optional[str] = None

class Team(TeamBase):
    id: int
    players: List[User] = []

    class Config:
        from_attributes = True 