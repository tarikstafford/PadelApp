from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models
from app.core import security
from app.crud.onboarding_crud import onboarding_crud
from app.database import get_db
from app.schemas.onboarding_schemas import (
    OnboardingCompleteWithInvitationRequest,
    OnboardingCompleteWithInvitationResponse,
    OnboardingProgressResponse,
    OnboardingProgressUpdate,
    OnboardingStatusResponse,
    OnboardingStatusUpdate,
)

router = APIRouter()


@router.post("/complete", response_model=OnboardingStatusResponse)
async def complete_onboarding(
    status_update: OnboardingStatusUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """
    Mark onboarding as completed for the current user.
    
    This endpoint allows users to mark their onboarding process as complete.
    It will set the onboarding_completed flag to True and record the completion timestamp.
    """
    try:
        # Update the user's onboarding status
        updated_user = onboarding_crud.update_status(
            db=db, user=current_user, status_update=status_update
        )

        # Return the updated onboarding status
        return OnboardingStatusResponse(
            id=updated_user.id,
            full_name=updated_user.full_name,
            email=updated_user.email,
            onboarding_completed=updated_user.onboarding_completed,
            onboarding_completed_at=updated_user.onboarding_completed_at,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update onboarding status: {str(e)}",
        )


@router.get("/status", response_model=OnboardingStatusResponse)
async def get_onboarding_status(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """
    Get the current onboarding status for the authenticated user.
    
    Returns the user's onboarding completion status and completion timestamp.
    """
    return OnboardingStatusResponse(
        id=current_user.id,
        full_name=current_user.full_name,
        email=current_user.email,
        onboarding_completed=current_user.onboarding_completed,
        onboarding_completed_at=current_user.onboarding_completed_at,
    )


@router.get("/progress", response_model=OnboardingProgressResponse)
async def get_onboarding_progress(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """
    Get detailed onboarding progress for the authenticated user.
    
    Returns a breakdown of onboarding steps and overall progress percentage.
    This includes:
    - Profile completion (name and email)
    - Skill assessment completion (ELO rating and preferred position set)
    - Preferences set (profile picture uploaded)
    - Tutorial completion (overall onboarding marked as complete)
    """
    progress_data = onboarding_crud.get_detailed_progress(current_user)

    return OnboardingProgressResponse(**progress_data)


@router.put("/progress", response_model=OnboardingProgressResponse)
async def update_onboarding_progress(
    progress_update: OnboardingProgressUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """
    Update onboarding progress for the authenticated user.
    
    This endpoint allows for updating specific onboarding progress items.
    Note: The actual progress is calculated from existing user data (profile, skills, etc.)
    so this endpoint primarily serves to trigger recalculation or future extensibility.
    """
    try:
        # Update progress (currently just returns user as-is since progress is calculated)
        updated_user = onboarding_crud.update_progress(
            db=db, user=current_user, progress_update=progress_update
        )

        # Get the updated progress data
        progress_data = onboarding_crud.get_detailed_progress(updated_user)

        return OnboardingProgressResponse(**progress_data)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update onboarding progress: {str(e)}",
        )


@router.post("/complete-with-invitation", response_model=OnboardingCompleteWithInvitationResponse)
async def complete_onboarding_with_invitation(
    request: OnboardingCompleteWithInvitationRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """
    Complete onboarding and immediately join the game from the invitation.
    
    This endpoint allows users to complete their onboarding process and automatically
    join the game they were invited to in a single action.
    """
    try:
        # Import here to avoid circular imports
        from app.crud.game_invitation_crud import game_invitation_crud

        # Complete onboarding and join game
        result = game_invitation_crud.complete_onboarding_and_join_game(
            db=db,
            token=request.invitation_token,
            user_id=current_user.id
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )

        # Build response
        response = OnboardingCompleteWithInvitationResponse(
            success=True,
            message="Onboarding completed and successfully joined the game!",
            user_id=current_user.id,
            onboarding_completed=True,
            game_id=result["game_id"],
            redirect_url=f"/games/{result['game_id']}"
        )

        return response

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete onboarding with invitation: {str(e)}",
        )
