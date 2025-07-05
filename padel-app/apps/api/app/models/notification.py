import enum
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy import (
    Enum as SAEnum,
)
from sqlalchemy.orm import relationship

from app.database import Base


class NotificationType(str, enum.Enum):
    GAME_STARTING = "GAME_STARTING"  # Game starting in 30min/1hr
    GAME_ENDED = "GAME_ENDED"  # Game time has ended
    SCORE_SUBMITTED = "SCORE_SUBMITTED"  # Score submitted by opposing team
    SCORE_CONFIRMED = "SCORE_CONFIRMED"  # Score confirmed by both teams
    SCORE_DISPUTED = "SCORE_DISPUTED"  # Score disputed by opposing team
    TEAM_INVITATION = "TEAM_INVITATION"  # Invited to join a team
    GAME_INVITATION = "GAME_INVITATION"  # Invited to join a game
    TOURNAMENT_REMINDER = "TOURNAMENT_REMINDER"  # Tournament starting soon
    ELO_UPDATE = "ELO_UPDATE"  # ELO rating changed
    GENERAL = "GENERAL"  # General notifications


class NotificationPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Notification content
    type = Column(
        SAEnum(NotificationType, name="notificationtype", create_enum=False),
        nullable=False,
    )
    priority = Column(
        SAEnum(NotificationPriority, name="notificationpriority", create_enum=False),
        default=NotificationPriority.MEDIUM,
        nullable=False,
    )
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)

    # Additional context data (game_id, team_id, etc.)
    data = Column(JSON, nullable=True)

    # Action link/route for frontend navigation
    action_url = Column(String(500), nullable=True)
    action_text = Column(String(100), nullable=True)  # "View Game", "Confirm Score", etc.

    # Status tracking
    read = Column(Boolean, default=False, nullable=False)
    read_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Auto-expire notifications after certain time
    expires_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="notifications")

    def mark_as_read(self):
        """Mark notification as read"""
        self.read = True
        self.read_at = datetime.utcnow()

    def is_expired(self) -> bool:
        """Check if notification has expired"""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    def __repr__(self):
        return f"<Notification(id={self.id}, user_id={self.user_id}, type='{self.type}', read={self.read})>"


class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)

    # Notification type preferences (enable/disable specific types)
    game_starting_enabled = Column(Boolean, default=True, nullable=False)
    game_ended_enabled = Column(Boolean, default=True, nullable=False)
    score_notifications_enabled = Column(Boolean, default=True, nullable=False)
    team_invitations_enabled = Column(Boolean, default=True, nullable=False)
    game_invitations_enabled = Column(Boolean, default=True, nullable=False)
    tournament_reminders_enabled = Column(Boolean, default=True, nullable=False)
    elo_updates_enabled = Column(Boolean, default=True, nullable=False)
    general_notifications_enabled = Column(Boolean, default=True, nullable=False)

    # Timing preferences
    game_reminder_minutes = Column(Integer, default=30, nullable=False)  # Remind X minutes before game

    # Delivery preferences (for future email/SMS integration)
    email_notifications_enabled = Column(Boolean, default=False, nullable=False)
    push_notifications_enabled = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="notification_preferences")

    def __repr__(self):
        return f"<NotificationPreference(id={self.id}, user_id={self.user_id})>"
