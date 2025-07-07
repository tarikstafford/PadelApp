from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel

from app.models.notification import NotificationPriority, NotificationType


# Base schemas
class NotificationBase(BaseModel):
    type: NotificationType
    priority: NotificationPriority
    title: str
    message: str
    data: Optional[dict[str, Any]] = None
    # action_url and action_text temporarily removed until migration


class NotificationPreferencesBase(BaseModel):
    game_starting_enabled: bool = True
    game_ended_enabled: bool = True
    score_notifications_enabled: bool = True
    team_invitations_enabled: bool = True
    game_invitations_enabled: bool = True
    tournament_reminders_enabled: bool = True
    elo_updates_enabled: bool = True
    general_notifications_enabled: bool = True
    game_reminder_minutes: int = 30
    email_notifications_enabled: bool = False
    push_notifications_enabled: bool = True


# Create schemas
class NotificationCreate(NotificationBase):
    user_id: int
    expires_at: Optional[datetime] = None


# Update schemas
class NotificationPreferencesUpdate(BaseModel):
    game_starting_enabled: Optional[bool] = None
    game_ended_enabled: Optional[bool] = None
    score_notifications_enabled: Optional[bool] = None
    team_invitations_enabled: Optional[bool] = None
    game_invitations_enabled: Optional[bool] = None
    tournament_reminders_enabled: Optional[bool] = None
    elo_updates_enabled: Optional[bool] = None
    general_notifications_enabled: Optional[bool] = None
    game_reminder_minutes: Optional[int] = None
    email_notifications_enabled: Optional[bool] = None
    push_notifications_enabled: Optional[bool] = None


# Response schemas
class NotificationResponse(NotificationBase):
    id: int
    user_id: int
    read: bool
    read_at: Optional[datetime] = None
    created_at: datetime
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NotificationPreferencesResponse(NotificationPreferencesBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    notifications: list[NotificationResponse]
    total_unread: int
    has_more: bool


# Request schemas
class MarkReadRequest(BaseModel):
    notification_ids: list[int]


class NotificationTestRequest(BaseModel):
    type: NotificationType
    title: str
    message: str
    target_user_id: Optional[int] = None  # For admin testing
