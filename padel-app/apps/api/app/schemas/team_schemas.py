from typing import Optional

from pydantic import BaseModel

from app.schemas.user_schemas import User


class TeamBase(BaseModel):
    name: str


class TeamCreate(TeamBase):
    pass


class TeamUpdate(TeamBase):
    name: Optional[str] = None


class Team(TeamBase):
    id: int
    players: list[User] = []

    class Config:
        from_attributes = True


class AddPlayerRequest(BaseModel):
    user_id: int


class RemovePlayerRequest(BaseModel):
    user_id: int
