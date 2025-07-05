from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.game_score import ConfirmationAction, ScoreStatus


# Base schemas
class GameScoreBase(BaseModel):
    team1_score: int = Field(..., ge=0, description="Score for team 1")
    team2_score: int = Field(..., ge=0, description="Score for team 2")


class ScoreConfirmationBase(BaseModel):
    action: ConfirmationAction
    counter_notes: Optional[str] = None


# Create schemas
class GameScoreCreate(GameScoreBase):
    game_id: int
    submitted_by_team: int = Field(..., ge=1, le=2, description="Team number (1 or 2)")


class ScoreConfirmationCreate(ScoreConfirmationBase):
    game_score_id: int
    confirming_team: int = Field(..., ge=1, le=2, description="Team number (1 or 2)")
    counter_team1_score: Optional[int] = Field(None, ge=0)
    counter_team2_score: Optional[int] = Field(None, ge=0)


# Update schemas
class GameScoreUpdate(BaseModel):
    final_team1_score: Optional[int] = Field(None, ge=0)
    final_team2_score: Optional[int] = Field(None, ge=0)
    admin_notes: Optional[str] = None


# Response schemas
class UserBasic(BaseModel):
    id: int
    full_name: str
    email: str

    class Config:
        from_attributes = True


class ScoreConfirmation(ScoreConfirmationBase):
    id: int
    game_score_id: int
    confirming_team: int
    confirming_user_id: int
    confirmed_at: datetime
    counter_team1_score: Optional[int] = None
    counter_team2_score: Optional[int] = None
    confirming_user: Optional[UserBasic] = None

    class Config:
        from_attributes = True


class GameScore(GameScoreBase):
    id: int
    game_id: int
    submitted_by_team: int
    submitted_by_user_id: int
    submitted_at: datetime
    status: ScoreStatus
    final_team1_score: Optional[int] = None
    final_team2_score: Optional[int] = None
    confirmed_at: Optional[datetime] = None
    admin_resolved: bool = False
    admin_notes: Optional[str] = None

    # Related data
    submitted_by: Optional[UserBasic] = None
    confirmations: list[ScoreConfirmation] = []

    class Config:
        from_attributes = True


# Request schemas for endpoints
class ScoreSubmissionRequest(GameScoreBase):
    submitted_by_team: int = Field(..., ge=1, le=2, description="Team number (1 or 2)")


class ScoreConfirmationRequest(BaseModel):
    action: ConfirmationAction = ConfirmationAction.CONFIRM


class ScoreCounterRequest(BaseModel):
    action: ConfirmationAction = ConfirmationAction.COUNTER
    counter_team1_score: int = Field(..., ge=0)
    counter_team2_score: int = Field(..., ge=0)
    counter_notes: Optional[str] = None


class AdminScoreResolutionRequest(BaseModel):
    final_team1_score: int = Field(..., ge=0)
    final_team2_score: int = Field(..., ge=0)
    admin_notes: Optional[str] = None


# Response schemas
class ScoreSubmissionResponse(BaseModel):
    success: bool
    message: str
    score: Optional[GameScore] = None
    can_confirm: bool = False


class ScoreConfirmationResponse(BaseModel):
    success: bool
    message: str
    score: Optional[GameScore] = None
    is_final: bool = False


class GameScoreListResponse(BaseModel):
    scores: list[GameScore]
    total_count: int
    latest_score: Optional[GameScore] = None


class ScoreStatusResponse(BaseModel):
    can_submit: bool
    can_confirm: bool
    message: str
    user_team: Optional[int] = None
    latest_score: Optional[GameScore] = None
