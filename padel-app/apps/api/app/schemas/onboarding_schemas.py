from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class OnboardingStatusUpdate(BaseModel):
    """Schema for updating onboarding completion status"""

    completed: bool = True


class OnboardingStatusResponse(BaseModel):
    """Schema for returning onboarding status"""

    id: int
    full_name: Optional[str] = None
    email: str
    onboarding_completed: bool
    onboarding_completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class OnboardingProgressUpdate(BaseModel):
    """Schema for updating detailed onboarding progress"""

    profile_completed: Optional[bool] = None
    skill_assessment_completed: Optional[bool] = None
    preferences_set: Optional[bool] = None
    tutorial_completed: Optional[bool] = None


class OnboardingProgressResponse(BaseModel):
    """Schema for returning detailed onboarding progress"""

    user_id: int
    profile_completed: bool = False
    skill_assessment_completed: bool = False
    preferences_set: bool = False
    tutorial_completed: bool = False
    overall_progress: float  # Percentage (0.0 to 1.0)

    model_config = {"from_attributes": True}


# Invitation-related onboarding schemas
class OnboardingCompleteWithInvitationRequest(BaseModel):
    """Schema for completing onboarding with an invitation context"""

    invitation_token: str
    completed: bool = True


class OnboardingCompleteWithInvitationResponse(BaseModel):
    """Schema for the response when completing onboarding with invitation"""

    success: bool
    message: str
    user_id: int
    onboarding_completed: bool
    game_id: Optional[int] = None
    redirect_url: Optional[str] = None
