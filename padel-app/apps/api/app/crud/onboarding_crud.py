from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.user import User as UserModel
from app.schemas.onboarding_schemas import OnboardingProgressUpdate, OnboardingStatusUpdate


def update_onboarding_status(
    db: Session, user: UserModel, status_update: OnboardingStatusUpdate
) -> UserModel:
    """Update user's onboarding completion status"""
    user.onboarding_completed = status_update.completed

    # Set completion timestamp if marking as completed
    if status_update.completed:
        user.onboarding_completed_at = datetime.utcnow()
    else:
        user.onboarding_completed_at = None

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_onboarding_status(db: Session, user_id: int) -> Optional[UserModel]:
    """Get user's onboarding status"""
    return db.query(UserModel).filter(UserModel.id == user_id).first()


def check_onboarding_completion(user: UserModel) -> bool:
    """Check if user has completed onboarding"""
    return user.onboarding_completed


def calculate_onboarding_progress(user: UserModel) -> float:
    """Calculate overall onboarding progress as a percentage (0.0 to 1.0)"""
    progress_items = []

    # Check basic profile completion
    profile_completed = bool(user.full_name and user.email)
    progress_items.append(profile_completed)

    # Check skill assessment completion (ELO rating set and preferred position)
    skill_assessment_completed = bool(
        user.elo_rating and user.elo_rating > 1.0 and user.preferred_position
    )
    progress_items.append(skill_assessment_completed)

    # Check preferences (profile picture uploaded)
    preferences_set = bool(user.profile_picture_url)
    progress_items.append(preferences_set)

    # Check tutorial completion (can be inferred from overall completion)
    tutorial_completed = user.onboarding_completed
    progress_items.append(tutorial_completed)

    # Calculate percentage
    completed_items = sum(progress_items)
    total_items = len(progress_items)

    return completed_items / total_items if total_items > 0 else 0.0


def get_detailed_onboarding_progress(user: UserModel) -> dict:
    """Get detailed onboarding progress breakdown"""
    profile_completed = bool(user.full_name and user.email)
    skill_assessment_completed = bool(
        user.elo_rating and user.elo_rating > 1.0 and user.preferred_position
    )
    preferences_set = bool(user.profile_picture_url)
    tutorial_completed = user.onboarding_completed

    return {
        "user_id": user.id,
        "profile_completed": profile_completed,
        "skill_assessment_completed": skill_assessment_completed,
        "preferences_set": preferences_set,
        "tutorial_completed": tutorial_completed,
        "overall_progress": calculate_onboarding_progress(user),
    }


def update_onboarding_progress(
    db: Session, user: UserModel, progress_update: OnboardingProgressUpdate
) -> UserModel:
    """Update specific onboarding progress items"""
    # This function doesn't directly update progress fields since they're calculated
    # from existing user data. However, we can use this to trigger recalculation
    # or potentially store progress in a separate model in the future.

    # For now, we'll just return the user as-is since progress is calculated
    # from existing fields like full_name, elo_rating, preferred_position, etc.
    return user


# Create a class-based CRUD interface following the pattern
class OnboardingCRUD:
    def update_status(
        self, db: Session, user: UserModel, status_update: OnboardingStatusUpdate
    ) -> UserModel:
        return update_onboarding_status(db, user, status_update)

    def get_status(self, db: Session, user_id: int) -> Optional[UserModel]:
        return get_onboarding_status(db, user_id)

    def check_completion(self, user: UserModel) -> bool:
        return check_onboarding_completion(user)

    def calculate_progress(self, user: UserModel) -> float:
        return calculate_onboarding_progress(user)

    def get_detailed_progress(self, user: UserModel) -> dict:
        return get_detailed_onboarding_progress(user)

    def update_progress(
        self, db: Session, user: UserModel, progress_update: OnboardingProgressUpdate
    ) -> UserModel:
        return update_onboarding_progress(db, user, progress_update)


# Create instance to be imported by other modules
onboarding_crud = OnboardingCRUD()
