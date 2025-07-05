
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import models
from app.core import security
from app.database import get_db
from app.models import Notification, NotificationPreference
from app.schemas.notification_schemas import (
    NotificationListResponse,
    NotificationPreferencesResponse,
    NotificationPreferencesUpdate,
)
from app.services.notification_service import notification_service

router = APIRouter()


@router.get("/", response_model=NotificationListResponse)
async def get_user_notifications(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
    skip: int = Query(0, ge=0, description="Number of notifications to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of notifications to return"),
    include_read: bool = Query(True, description="Include read notifications"),
):
    """Get notifications for the current user"""

    notifications = notification_service.get_user_notifications(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        include_read=include_read
    )

    unread_count = notification_service.get_unread_count(db, current_user.id)

    return NotificationListResponse(
        notifications=notifications,
        total_unread=unread_count,
        has_more=len(notifications) == limit
    )


@router.get("/unread-count")
async def get_unread_notification_count(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """Get the count of unread notifications for the current user"""

    unread_count = notification_service.get_unread_count(db, current_user.id)

    return {
        "unread_count": unread_count
    }


@router.post("/{notification_id}/mark-read")
async def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """Mark a specific notification as read"""

    success = notification_service.mark_notification_read(
        db=db,
        notification_id=notification_id,
        user_id=current_user.id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    return {"message": "Notification marked as read"}


@router.post("/mark-all-read")
async def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """Mark all notifications as read for the current user"""

    count = notification_service.mark_all_notifications_read(db, current_user.id)

    return {
        "message": f"Marked {count} notifications as read"
    }


@router.get("/preferences", response_model=NotificationPreferencesResponse)
async def get_notification_preferences(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """Get user's notification preferences"""

    preferences = (
        db.query(NotificationPreference)
        .filter(NotificationPreference.user_id == current_user.id)
        .first()
    )

    if not preferences:
        # Create default preferences
        preferences = NotificationPreference(user_id=current_user.id)
        db.add(preferences)
        db.commit()
        db.refresh(preferences)

    return preferences


@router.put("/preferences", response_model=NotificationPreferencesResponse)
async def update_notification_preferences(
    preferences_update: NotificationPreferencesUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """Update user's notification preferences"""

    preferences = (
        db.query(NotificationPreference)
        .filter(NotificationPreference.user_id == current_user.id)
        .first()
    )

    if not preferences:
        # Create new preferences
        preferences = NotificationPreference(user_id=current_user.id)
        db.add(preferences)

    # Update preferences with provided values
    update_data = preferences_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(preferences, field, value)

    db.commit()
    db.refresh(preferences)

    return preferences


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """Delete a specific notification"""

    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id,
            Notification.user_id == current_user.id
        )
        .first()
    )

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    db.delete(notification)
    db.commit()

    return {"message": "Notification deleted"}


@router.post("/cleanup-expired")
async def cleanup_expired_notifications(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_admin_user),
):
    """Admin endpoint to cleanup expired notifications"""

    count = notification_service.cleanup_expired_notifications(db)

    return {
        "message": f"Cleaned up {count} expired notifications"
    }
