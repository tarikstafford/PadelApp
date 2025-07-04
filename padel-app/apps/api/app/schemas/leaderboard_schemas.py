from typing import Optional

from pydantic import BaseModel


class LeaderboardUserResponse(BaseModel):
    id: int
    full_name: str
    avatar_url: Optional[str] = None
    club_name: Optional[str] = None
    elo_rating: float

    class Config:
        from_attributes = True


class LeaderboardResponse(BaseModel):
    total: int
    offset: int
    limit: int
    users: list[LeaderboardUserResponse]
