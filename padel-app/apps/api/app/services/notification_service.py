import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app import crud
from app.models import Notification, NotificationPreference
from app.models.notification import NotificationPriority, NotificationType

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for managing user notifications"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def create_notification(
        self,
        db: Session,
        user_id: int,
        notification_type: NotificationType,
        title: str,
        message: str,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        data: Optional[dict] = None,
        action_url: Optional[str] = None,
        action_text: Optional[str] = None,
        expires_in_hours: Optional[int] = None,
    ) -> Notification:
        """Create a new notification for a user"""

        # Check user's notification preferences
        preferences = self._get_user_preferences(db, user_id)
        if not self._should_send_notification(notification_type, preferences):
            self.logger.info(
                f"Notification type {notification_type} disabled for user {user_id}"
            )
            return None

        expires_at = None
        if expires_in_hours:
            expires_at = datetime.now(timezone.utc) + timedelta(hours=expires_in_hours)

        notification = Notification(
            user_id=user_id,
            type=notification_type,
            priority=priority,
            title=title,
            message=message,
            data=data or {},
            action_url=action_url,
            action_text=action_text,
            expires_at=expires_at,
        )

        db.add(notification)
        db.commit()
        db.refresh(notification)

        self.logger.info(
            f"Created notification {notification.id} for user {user_id}: {title}"
        )
        return notification

    def send_game_starting_notifications(
        self, db: Session, game_id: int
    ) -> list[Notification]:
        """Send notifications to all game participants that the game is starting"""
        game = crud.game_crud.get_game(db, game_id)
        if not game:
            self.logger.warning(f"Game {game_id} not found for starting notifications")
            return []

        notifications = []
        club_name = (
            game.booking.court.club.name
            if game.booking and game.booking.court and game.booking.court.club
            else "Unknown Club"
        )

        for game_player in game.players:
            if game_player.status.value == "ACCEPTED":  # Only notify accepted players
                notification = self.create_notification(
                    db=db,
                    user_id=game_player.user_id,
                    notification_type=NotificationType.GAME_STARTING,
                    title="Game Starting Soon!",
                    message=f"Your game at {club_name} starts in 30 minutes",
                    priority=NotificationPriority.HIGH,
                    data={
                        "game_id": game_id,
                        "club_name": club_name,
                        "start_time": game.start_time.isoformat(),
                    },
                    action_url=f"/games/{game_id}",
                    action_text="View Game",
                    expires_in_hours=2,
                )
                if notification:
                    notifications.append(notification)

        return notifications

    def send_game_ended_notifications(
        self, db: Session, game_id: int
    ) -> list[Notification]:
        """Send notifications to all game participants that the game has ended"""
        game = crud.game_crud.get_game(db, game_id)
        if not game:
            self.logger.warning(f"Game {game_id} not found for ended notifications")
            return []

        notifications = []
        club_name = (
            game.booking.court.club.name
            if game.booking and game.booking.court and game.booking.court.club
            else "Unknown Club"
        )

        for game_player in game.players:
            if game_player.status.value == "ACCEPTED":
                notification = self.create_notification(
                    db=db,
                    user_id=game_player.user_id,
                    notification_type=NotificationType.GAME_ENDED,
                    title="Game Time Complete",
                    message=f"Your game at {club_name} has ended. Don't forget to submit the score!",
                    priority=NotificationPriority.MEDIUM,
                    data={
                        "game_id": game_id,
                        "club_name": club_name,
                        "end_time": game.end_time.isoformat(),
                    },
                    action_url=f"/games/{game_id}",
                    action_text="Submit Score",
                    expires_in_hours=24,
                )
                if notification:
                    notifications.append(notification)

        return notifications

    def send_score_submitted_notifications(
        self, db: Session, game_id: int, score_id: int, submitting_team: int
    ) -> list[Notification]:
        """Send notifications to opposing team that a score was submitted"""
        game = crud.game_crud.get_game(db, game_id)
        if not game:
            return []

        # Determine which team to notify (the opposing team)
        target_team_id = 2 if submitting_team == 1 else 1
        target_team = game.team1 if target_team_id == 1 else game.team2

        if not target_team:
            return []

        notifications = []
        for player in target_team.players:
            notification = self.create_notification(
                db=db,
                user_id=player.id,
                notification_type=NotificationType.SCORE_SUBMITTED,
                title="Score Submitted",
                message="The opposing team has submitted a score for your game. Please confirm or dispute it.",
                priority=NotificationPriority.HIGH,
                data={
                    "game_id": game_id,
                    "score_id": score_id,
                    "submitting_team": submitting_team,
                },
                action_url=f"/games/{game_id}/scores/{score_id}",
                action_text="Review Score",
                expires_in_hours=48,
            )
            if notification:
                notifications.append(notification)

        return notifications

    def send_score_confirmed_notifications(
        self, db: Session, game_id: int
    ) -> list[Notification]:
        """Send notifications to all players that the score has been confirmed"""
        game = crud.game_crud.get_game(db, game_id)
        if not game:
            return []

        notifications = []
        all_players = []

        # Collect all players from both teams
        if game.team1:
            all_players.extend(game.team1.players)
        if game.team2:
            all_players.extend(game.team2.players)

        for player in all_players:
            notification = self.create_notification(
                db=db,
                user_id=player.id,
                notification_type=NotificationType.SCORE_CONFIRMED,
                title="Score Confirmed",
                message="The game score has been confirmed by both teams. ELO ratings have been updated.",
                priority=NotificationPriority.MEDIUM,
                data={
                    "game_id": game_id,
                },
                action_url=f"/games/{game_id}",
                action_text="View Game",
                expires_in_hours=48,
            )
            if notification:
                notifications.append(notification)

        return notifications

    def send_team_invitation_notification(
        self, db: Session, user_id: int, team_id: int, invited_by_id: int
    ) -> Optional[Notification]:
        """Send notification for team invitation"""
        team = crud.team_crud.get_team(db, team_id)
        invited_by = crud.user_crud.get_user(db, invited_by_id)

        if not team or not invited_by:
            return None

        return self.create_notification(
            db=db,
            user_id=user_id,
            notification_type=NotificationType.TEAM_INVITATION,
            title="Team Invitation",
            message=f"{invited_by.full_name} has invited you to join team '{team.name}'",
            priority=NotificationPriority.MEDIUM,
            data={
                "team_id": team_id,
                "invited_by_id": invited_by_id,
                "team_name": team.name,
            },
            action_url=f"/teams/{team_id}/invitation",
            action_text="View Invitation",
            expires_in_hours=72,
        )

    def mark_notification_read(
        self, db: Session, notification_id: int, user_id: int
    ) -> bool:
        """Mark a notification as read"""
        notification = (
            db.query(Notification)
            .filter(Notification.id == notification_id, Notification.user_id == user_id)
            .first()
        )

        if not notification:
            return False

        notification.mark_as_read()
        db.commit()
        return True

    def mark_all_notifications_read(self, db: Session, user_id: int) -> int:
        """Mark all notifications as read for a user"""
        unread_notifications = (
            db.query(Notification)
            .filter(Notification.user_id == user_id, Notification.read == False)
            .all()
        )

        count = 0
        for notification in unread_notifications:
            notification.mark_as_read()
            count += 1

        db.commit()
        return count

    def get_user_notifications(
        self,
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 50,
        include_read: bool = True,
    ) -> list[Notification]:
        """Get notifications for a user"""
        query = db.query(Notification).filter(Notification.user_id == user_id)

        if not include_read:
            query = query.filter(Notification.read == False)

        # Filter out expired notifications
        query = query.filter(
            or_(
                Notification.expires_at.is_(None),
                Notification.expires_at > datetime.now(timezone.utc),
            )
        )

        return (
            query.order_by(Notification.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_unread_count(self, db: Session, user_id: int) -> int:
        """Get count of unread notifications for a user"""
        return (
            db.query(Notification)
            .filter(
                Notification.user_id == user_id,
                Notification.read == False,
                or_(
                    Notification.expires_at.is_(None),
                    Notification.expires_at > datetime.now(timezone.utc),
                ),
            )
            .count()
        )

    def _get_user_preferences(
        self, db: Session, user_id: int
    ) -> NotificationPreference:
        """Get user's notification preferences, creating default if none exist"""
        preferences = (
            db.query(NotificationPreference)
            .filter(NotificationPreference.user_id == user_id)
            .first()
        )

        if not preferences:
            # Create default preferences
            preferences = NotificationPreference(user_id=user_id)
            db.add(preferences)
            db.commit()
            db.refresh(preferences)

        return preferences

    def _should_send_notification(
        self, notification_type: NotificationType, preferences: NotificationPreference
    ) -> bool:
        """Check if notification should be sent based on user preferences"""
        type_to_preference = {
            NotificationType.GAME_STARTING: preferences.game_starting_enabled,
            NotificationType.GAME_ENDED: preferences.game_ended_enabled,
            NotificationType.SCORE_SUBMITTED: preferences.score_notifications_enabled,
            NotificationType.SCORE_CONFIRMED: preferences.score_notifications_enabled,
            NotificationType.SCORE_DISPUTED: preferences.score_notifications_enabled,
            NotificationType.TEAM_INVITATION: preferences.team_invitations_enabled,
            NotificationType.GAME_INVITATION: preferences.game_invitations_enabled,
            NotificationType.TOURNAMENT_REMINDER: preferences.tournament_reminders_enabled,
            NotificationType.ELO_UPDATE: preferences.elo_updates_enabled,
            NotificationType.GENERAL: preferences.general_notifications_enabled,
        }

        return type_to_preference.get(notification_type, True)

    def cleanup_expired_notifications(self, db: Session) -> int:
        """Clean up expired notifications"""
        expired_notifications = (
            db.query(Notification)
            .filter(
                Notification.expires_at.isnot(None),
                Notification.expires_at <= datetime.now(timezone.utc),
            )
            .all()
        )

        count = len(expired_notifications)
        for notification in expired_notifications:
            db.delete(notification)

        db.commit()
        self.logger.info(f"Cleaned up {count} expired notifications")
        return count


# Global service instance
notification_service = NotificationService()
