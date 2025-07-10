from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.team_membership import TeamMembershipRole, TeamMembershipStatus
from app.schemas.user_schemas import User


class TeamBase(BaseModel):
    name: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: bool = True


class TeamCreate(TeamBase):
    pass


class TeamUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: Optional[bool] = None


class Team(TeamBase):
    id: int
    created_by: int
    created_at: datetime
    players: list[User] = []

    class Config:
        from_attributes = True


class AddPlayerRequest(BaseModel):
    user_id: int


class RemovePlayerRequest(BaseModel):
    user_id: int


# Team Membership Schemas
class TeamMembershipBase(BaseModel):
    role: TeamMembershipRole = TeamMembershipRole.MEMBER
    status: TeamMembershipStatus = TeamMembershipStatus.ACTIVE


class TeamMembershipCreate(TeamMembershipBase):
    user_id: int
    team_id: int


class TeamMembershipUpdate(BaseModel):
    role: Optional[TeamMembershipRole] = None
    status: Optional[TeamMembershipStatus] = None


class TeamMembershipResponse(TeamMembershipBase):
    id: int
    team_id: int
    user_id: int
    joined_at: datetime
    left_at: Optional[datetime] = None
    is_active: bool
    user: User

    class Config:
        from_attributes = True


class TeamWithMembers(Team):
    team_memberships: list[TeamMembershipResponse] = []


# Team History Schemas
class TeamGameHistoryResponse(BaseModel):
    id: int
    team_id: int
    game_id: int
    won: bool
    points_scored: int
    points_conceded: int
    opponent_team_id: Optional[int] = None
    elo_before: Optional[float] = None
    elo_after: Optional[float] = None
    elo_change: Optional[float] = None
    game_date: datetime
    is_tournament_game: bool
    tournament_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TeamStatsResponse(BaseModel):
    id: int
    team_id: int
    games_played: int
    games_won: int
    games_lost: int
    total_points_scored: int
    total_points_conceded: int
    current_average_elo: Optional[float] = None
    peak_average_elo: Optional[float] = None
    lowest_average_elo: Optional[float] = None
    tournaments_participated: int
    tournaments_won: int
    tournament_matches_won: int
    tournament_matches_lost: int
    current_win_streak: int
    current_loss_streak: int
    longest_win_streak: int
    longest_loss_streak: int
    last_game_date: Optional[datetime] = None
    last_updated: datetime
    created_at: datetime
    class Config:
        from_attributes = True

    @property
    def win_rate(self) -> float:
        """Calculate win rate percentage"""
        if self.games_played == 0:
            return 0.0
        return (self.games_won / self.games_played) * 100

    @property
    def points_per_game(self) -> float:
        """Calculate average points scored per game"""
        if self.games_played == 0:
            return 0.0
        return self.total_points_scored / self.games_played

    @property
    def points_conceded_per_game(self) -> float:
        """Calculate average points conceded per game"""
        if self.games_played == 0:
            return 0.0
        return self.total_points_conceded / self.games_played

    @property
    def point_differential(self) -> int:
        """Calculate total point differential (scored - conceded)"""
        return self.total_points_scored - self.total_points_conceded

    @property
    def tournament_win_rate(self) -> float:
        """Calculate tournament win rate percentage"""
        if self.tournaments_participated == 0:
            return 0.0
        return (self.tournaments_won / self.tournaments_participated) * 100
