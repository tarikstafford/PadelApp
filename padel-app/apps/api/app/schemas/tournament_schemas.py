from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator

from app.models.tournament import (
    MatchStatus,
    TournamentCategory,
    TournamentStatus,
    TournamentType,
)


# Base schemas
class TournamentCategoryCreate(BaseModel):
    category: TournamentCategory
    max_participants: int = Field(
        gt=0, description="Maximum number of participants for this category"
    )


class TournamentCategoryResponse(BaseModel):
    id: int
    category: TournamentCategory
    max_participants: int
    min_elo: float
    max_elo: float
    current_participants: int = 0

    class Config:
        from_attributes = True


# Tournament schemas
class TournamentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    tournament_type: TournamentType
    start_date: datetime
    end_date: datetime
    registration_deadline: datetime
    max_participants: int = Field(gt=0)
    entry_fee: Optional[float] = Field(ge=0, default=0.0)
    categories: list[TournamentCategoryCreate] = Field(
        min_items=1, description="At least one category is required"
    )
    court_ids: list[int] = Field(
        description="List of court IDs to be used for the tournament"
    )

    @field_validator("end_date")
    @classmethod
    def end_date_after_start_date(cls, v, info):
        if info.data.get("start_date") and v <= info.data["start_date"]:
            raise ValueError("End date must be after start date")
        return v

    @field_validator("registration_deadline")
    @classmethod
    def registration_deadline_before_start(cls, v, info):
        if info.data.get("start_date") and v >= info.data["start_date"]:
            raise ValueError("Registration deadline must be before start date")
        return v


class TournamentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    registration_deadline: Optional[datetime] = None
    max_participants: Optional[int] = Field(None, gt=0)
    entry_fee: Optional[float] = Field(None, ge=0)
    status: Optional[TournamentStatus] = None


class TournamentResponse(BaseModel):
    id: int
    club_id: int
    name: str
    description: Optional[str]
    tournament_type: TournamentType
    start_date: datetime
    end_date: datetime
    registration_deadline: datetime
    status: TournamentStatus
    max_participants: int
    entry_fee: float
    created_at: datetime
    updated_at: datetime
    categories: list[TournamentCategoryResponse] = []
    total_registered_teams: int = 0

    class Config:
        from_attributes = True


class TournamentListResponse(BaseModel):
    id: int
    name: str
    tournament_type: TournamentType
    start_date: datetime
    end_date: datetime
    status: TournamentStatus
    total_registered_teams: int
    max_participants: int
    entry_fee: Optional[float] = None
    club_name: Optional[str] = None

    class Config:
        from_attributes = True


# Team registration schemas
class TournamentTeamCreate(BaseModel):
    team_id: int
    category: TournamentCategory


class TournamentTeamResponse(BaseModel):
    id: int
    team_id: int
    team_name: str
    category: TournamentCategory
    seed: Optional[int]
    average_elo: float
    registration_date: datetime
    is_active: bool
    players: list[dict[str, Any]] = []  # Will contain player info

    class Config:
        from_attributes = True


# Match schemas
class TournamentMatchCreate(BaseModel):
    team1_id: Optional[int] = None
    team2_id: Optional[int] = None
    round_number: int = Field(gt=0)
    match_number: int = Field(gt=0)
    scheduled_time: Optional[datetime] = None
    court_id: Optional[int] = None


class TournamentMatchUpdate(BaseModel):
    scheduled_time: Optional[datetime] = None
    court_id: Optional[int] = None
    status: Optional[MatchStatus] = None
    team1_score: Optional[int] = Field(None, ge=0)
    team2_score: Optional[int] = Field(None, ge=0)
    winning_team_id: Optional[int] = None


class TournamentMatchResponse(BaseModel):
    id: int
    tournament_id: int
    category: TournamentCategory
    team1_id: Optional[int]
    team2_id: Optional[int]
    team1_name: Optional[str]
    team2_name: Optional[str]
    round_number: int
    match_number: int
    scheduled_time: Optional[datetime]
    court_id: Optional[int]
    court_name: Optional[str]
    status: MatchStatus
    winning_team_id: Optional[int]
    team1_score: Optional[int]
    team2_score: Optional[int]
    winner_advances_to_match_id: Optional[int]
    loser_advances_to_match_id: Optional[int]

    class Config:
        from_attributes = True


# Bracket schemas
class BracketNode(BaseModel):
    match_id: Optional[int]
    team1_id: Optional[int]
    team2_id: Optional[int]
    team1_name: Optional[str]
    team2_name: Optional[str]
    winning_team_id: Optional[int]
    round_number: int
    match_number: int
    status: MatchStatus
    team1_score: Optional[int] = None
    team2_score: Optional[int] = None


class TournamentBracket(BaseModel):
    tournament_id: int
    category: TournamentCategory
    tournament_type: TournamentType
    rounds: dict[int, list[BracketNode]]  # round_number -> list of matches
    total_rounds: int


# Court booking schemas
class TournamentCourtBookingCreate(BaseModel):
    court_id: int
    start_time: datetime
    end_time: datetime


class TournamentCourtBookingResponse(BaseModel):
    id: int
    court_id: int
    court_name: str
    start_time: datetime
    end_time: datetime
    is_occupied: bool
    match_id: Optional[int]

    class Config:
        from_attributes = True


# Trophy schemas
class TournamentTrophyResponse(BaseModel):
    id: int
    tournament_id: int
    tournament_name: str
    category: TournamentCategory
    user_id: int
    team_id: int
    position: int
    trophy_type: str
    awarded_at: datetime

    class Config:
        from_attributes = True


# Eligibility check schemas
class TeamEligibilityCheck(BaseModel):
    team_id: int
    average_elo: float
    eligible_categories: list[TournamentCategory]
    reasons: dict[TournamentCategory, str]  # Category -> reason if not eligible


class TournamentEligibilityResponse(BaseModel):
    tournament_id: int
    teams: list[TeamEligibilityCheck]


# Statistics schemas
class TournamentStats(BaseModel):
    tournament_id: int
    total_matches: int
    completed_matches: int
    pending_matches: int
    total_teams: int
    categories_breakdown: dict[TournamentCategory, int]
    average_match_duration: Optional[float]  # in minutes
    completion_percentage: float


# Admin dashboard schemas
class TournamentDashboard(BaseModel):
    tournaments: list[TournamentListResponse]
    upcoming_matches: list[TournamentMatchResponse]
    recent_results: list[TournamentMatchResponse]
    stats: dict[str, Any]
