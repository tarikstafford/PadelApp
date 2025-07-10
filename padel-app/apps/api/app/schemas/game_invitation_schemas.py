from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class GameInvitationCreate(BaseModel):
    expires_in_hours: Optional[int] = 24
    max_uses: Optional[int] = None


class GameInvitationResponse(BaseModel):
    id: int
    game_id: int
    token: str
    created_at: datetime
    expires_at: datetime
    is_active: bool
    max_uses: Optional[int]
    current_uses: int
    invite_url: str

    model_config = {"from_attributes": True}


class GameInvitationAccept(BaseModel):
    """Schema for accepting a game invitation"""

    # No additional data needed, just the token from URL


class GameInvitationInfo(BaseModel):
    """Public info about an invitation (before accepting)"""

    game_id: int
    game_name: str
    creator_name: str
    start_time: datetime
    end_time: datetime
    court_name: str
    club_name: str
    current_players: int
    max_players: int
    is_valid: bool
    expires_at: datetime

    model_config = {"from_attributes": True}


# Team Invitation Schemas
class TeamInviteRequest(BaseModel):
    team_id: int


class TeamInvitationResponse(BaseModel):
    message: str
    team_id: int
    team_name: str
    invited_members: int
    game_id: int


# Onboarding-related invitation schemas
class OnboardingRequiredResponse(BaseModel):
    """Response when user needs to complete onboarding before joining game"""

    success: bool = False
    message: str
    requires_onboarding: bool = True
    game_id: int
    invitation_token: str
    onboarding_redirect_url: str


class CompleteOnboardingWithInvitation(BaseModel):
    """Schema for completing onboarding with an invitation context"""

    invitation_token: str
    completed: bool = True
