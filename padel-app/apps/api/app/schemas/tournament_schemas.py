from datetime import datetime, timedelta
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator

from app.models.tournament import (
    MatchStatus,
    RecurrencePattern,
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
    current_teams: int = 0  # For team tournaments
    current_individuals: int = 0  # For Americano tournaments

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
    total_registered_participants: int = 0  # For Americano tournaments
    requires_teams: bool = True  # Computed based on tournament type

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
    categories: list[TournamentCategoryResponse] = []

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


# Individual participant registration schemas (for Americano tournaments)
class TournamentParticipantCreate(BaseModel):
    category: TournamentCategory


class TournamentParticipantResponse(BaseModel):
    id: int
    user_id: int
    user_name: str
    user_email: str
    category: TournamentCategory
    seed_position: Optional[int]
    elo_at_registration: float
    registration_date: datetime
    is_active: bool
    match_teams: Optional[dict[str, Any]] = None  # Temporary team assignments

    class Config:
        from_attributes = True


class TournamentRegistrationRequest(BaseModel):
    """Generic registration request that can handle both teams and individuals"""

    category: TournamentCategory
    team_id: Optional[int] = None  # For team tournaments

    @field_validator("team_id")
    @classmethod
    def validate_team_id(cls, v, info):
        # team_id is required for non-Americano tournaments
        # This will be validated server-side based on tournament type
        return v


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


# Recurring tournament schemas
class RecurringTournamentCategoryTemplateCreate(BaseModel):
    category: TournamentCategory
    max_participants: int = Field(gt=0)
    min_elo: float = Field(ge=1.0)
    max_elo: float = Field(ge=1.0)

    @field_validator("max_elo")
    @classmethod
    def max_elo_greater_than_min(cls, v, info):
        if info.data.get("min_elo") and v <= info.data["min_elo"]:
            raise ValueError("Max ELO must be greater than min ELO")
        return v


class RecurringTournamentCategoryTemplateResponse(BaseModel):
    id: int
    category: TournamentCategory
    max_participants: int
    min_elo: float
    max_elo: float

    class Config:
        from_attributes = True


class RecurringTournamentCreate(BaseModel):
    series_name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    recurrence_pattern: RecurrencePattern
    interval_value: int = Field(ge=1, default=1)
    days_of_week: Optional[list[int]] = Field(
        None, description="Days of week (0=Monday, 6=Sunday)"
    )
    day_of_month: Optional[int] = Field(None, ge=1, le=31)
    series_start_date: datetime
    series_end_date: Optional[datetime] = None
    tournament_type: TournamentType
    duration_hours: int = Field(ge=1, le=24, default=3)
    registration_deadline_hours: int = Field(ge=1, le=168, default=24)
    max_participants: int = Field(gt=0)
    entry_fee: Optional[float] = Field(ge=0, default=0.0)
    advance_generation_days: int = Field(ge=7, le=365, default=30)
    auto_generation_enabled: bool = True
    category_templates: list[RecurringTournamentCategoryTemplateCreate] = Field(
        min_items=1, description="At least one category template is required"
    )

    @field_validator("series_end_date")
    @classmethod
    def series_end_after_start(cls, v, info):
        if (
            v
            and info.data.get("series_start_date")
            and v <= info.data["series_start_date"]
        ):
            raise ValueError("Series end date must be after start date")
        return v

    @field_validator("days_of_week")
    @classmethod
    def valid_days_of_week(cls, v, info):
        if v is not None:
            if not v or len(v) == 0:
                raise ValueError("Days of week cannot be empty if specified")
            if not all(0 <= day <= 6 for day in v):
                raise ValueError(
                    "Days of week must be between 0 (Monday) and 6 (Sunday)"
                )
            if len(v) != len(set(v)):
                raise ValueError("Days of week must be unique")
        return v

    @field_validator("day_of_month")
    @classmethod
    def valid_day_of_month(cls, v, info):
        if (
            v is not None
            and info.data.get("recurrence_pattern") == RecurrencePattern.MONTHLY
        ):
            if not 1 <= v <= 31:
                raise ValueError("Day of month must be between 1 and 31")
        return v


class RecurringTournamentUpdate(BaseModel):
    series_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    interval_value: Optional[int] = Field(None, ge=1)
    days_of_week: Optional[list[int]] = Field(
        None, description="Days of week (0=Monday, 6=Sunday)"
    )
    day_of_month: Optional[int] = Field(None, ge=1, le=31)
    series_end_date: Optional[datetime] = None
    duration_hours: Optional[int] = Field(None, ge=1, le=24)
    registration_deadline_hours: Optional[int] = Field(None, ge=1, le=168)
    max_participants: Optional[int] = Field(None, gt=0)
    entry_fee: Optional[float] = Field(None, ge=0)
    advance_generation_days: Optional[int] = Field(None, ge=7, le=365)
    auto_generation_enabled: Optional[bool] = None
    is_active: Optional[bool] = None
    category_templates: Optional[list[RecurringTournamentCategoryTemplateCreate]] = None

    @field_validator("days_of_week")
    @classmethod
    def valid_days_of_week(cls, v):
        if v is not None:
            if not v or len(v) == 0:
                raise ValueError("Days of week cannot be empty if specified")
            if not all(0 <= day <= 6 for day in v):
                raise ValueError(
                    "Days of week must be between 0 (Monday) and 6 (Sunday)"
                )
            if len(v) != len(set(v)):
                raise ValueError("Days of week must be unique")
        return v


class RecurringTournamentResponse(BaseModel):
    id: int
    club_id: int
    series_name: str
    description: Optional[str]
    recurrence_pattern: RecurrencePattern
    interval_value: int
    days_of_week: Optional[list[int]]
    day_of_month: Optional[int]
    series_start_date: datetime
    series_end_date: Optional[datetime]
    tournament_type: TournamentType
    duration_hours: int
    registration_deadline_hours: int
    max_participants: int
    entry_fee: float
    advance_generation_days: int
    auto_generation_enabled: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    category_templates: list[RecurringTournamentCategoryTemplateResponse] = []
    total_instances: int = 0
    upcoming_instances: int = 0

    class Config:
        from_attributes = True


class RecurringTournamentListResponse(BaseModel):
    id: int
    series_name: str
    recurrence_pattern: RecurrencePattern
    tournament_type: TournamentType
    series_start_date: datetime
    series_end_date: Optional[datetime]
    is_active: bool
    total_instances: int
    upcoming_instances: int
    club_name: Optional[str] = None

    class Config:
        from_attributes = True


class RecurringTournamentInstancesResponse(BaseModel):
    recurring_tournament_id: int
    series_name: str
    instances: list[TournamentListResponse]
    total_count: int
    next_occurrences: list[datetime] = []


class RecurringTournamentGenerateRequest(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(ge=1, le=100, default=10)


class RecurringTournamentGenerateResponse(BaseModel):
    recurring_tournament_id: int
    generated_tournaments: list[TournamentListResponse]
    total_generated: int
    next_occurrence_dates: list[datetime] = []


class RecurringTournamentNextOccurrences(BaseModel):
    recurring_tournament_id: int
    series_name: str
    next_occurrences: list[datetime]


class RecurringTournamentStats(BaseModel):
    recurring_tournament_id: int
    series_name: str
    total_instances: int
    completed_instances: int
    cancelled_instances: int
    upcoming_instances: int
    total_participants: int
    average_participants_per_instance: float
    completion_rate: float  # Percentage of completed vs total instances


# Hourly time slot schemas
class HourlyTimeSlot(BaseModel):
    start_time: datetime
    end_time: datetime
    day_of_week: int = Field(ge=0, le=6, description="0=Monday, 6=Sunday")
    hour: int = Field(ge=0, le=23, description="Hour of the day (0-23)")

    @field_validator("end_time")
    @classmethod
    def validate_hourly_slot(cls, v, info):
        if info.data.get("start_time"):
            start_time = info.data["start_time"]
            expected_end = start_time.replace(
                minute=0, second=0, microsecond=0
            ) + timedelta(hours=1)
            if v != expected_end:
                raise ValueError("Time slot must be exactly 1 hour long")
        return v

    @field_validator("hour")
    @classmethod
    def validate_hour_matches_time(cls, v, info):
        if info.data.get("start_time"):
            start_time = info.data["start_time"]
            if v != start_time.hour:
                raise ValueError("Hour field must match the hour of start_time")
        return v


class TournamentScheduleRequest(BaseModel):
    tournament_id: int
    time_slots: list[HourlyTimeSlot] = Field(
        min_items=1, description="List of selected hourly time slots"
    )
    court_ids: list[int] = Field(
        min_items=1, description="List of court IDs to be used for the tournament"
    )
    auto_schedule: bool = Field(
        default=True, description="Whether to automatically schedule matches"
    )

    @field_validator("time_slots")
    @classmethod
    def validate_time_slots_sequential(cls, v):
        if len(v) < 1:
            raise ValueError("At least one time slot is required")

        # Sort by start time
        sorted_slots = sorted(v, key=lambda x: x.start_time)

        # Check for overlaps
        for i in range(len(sorted_slots) - 1):
            if sorted_slots[i].end_time > sorted_slots[i + 1].start_time:
                raise ValueError("Time slots cannot overlap")

        return v


class TournamentScheduleResponse(BaseModel):
    tournament_id: int
    schedule: dict[str, Any]
    total_matches: int
    total_time_slots: int
    courts_required: int
    estimated_duration: int  # in hours
    court_bookings_created: int
    success: bool
    message: Optional[str] = None


class CourtAvailabilityRequest(BaseModel):
    court_ids: list[int]
    time_slots: list[HourlyTimeSlot]
    exclude_tournament_id: Optional[int] = None


class CourtAvailabilityResponse(BaseModel):
    available_courts: list[int]
    unavailable_courts: list[int]
    availability_details: dict[
        int, list[dict[str, Any]]
    ]  # court_id -> availability info


class TournamentScheduleCalculation(BaseModel):
    tournament_type: TournamentType
    categories: list[TournamentCategory]
    participants_per_category: dict[TournamentCategory, int]
    available_courts: list[int]
    time_slots: list[HourlyTimeSlot]


class TournamentScheduleCalculationResponse(BaseModel):
    total_matches: int
    matches_per_category: dict[TournamentCategory, int]
    courts_per_slot: int
    total_time_slots: int
    recommended_courts: list[int]
    feasible: bool
    warnings: list[str] = []


class TournamentCourtBookingBulkCreate(BaseModel):
    tournament_id: int
    court_bookings: list[TournamentCourtBookingCreate]


class TournamentCourtBookingBulkResponse(BaseModel):
    tournament_id: int
    created_bookings: list[TournamentCourtBookingResponse]
    failed_bookings: list[dict[str, Any]]
    total_created: int
    total_failed: int


class TournamentScheduleSummary(BaseModel):
    tournament_id: int
    tournament_name: str
    total_court_bookings: int
    total_matches: int
    start_date: datetime
    end_date: datetime
    court_bookings: list[dict[str, Any]]
    matches_by_status: dict[str, int]
