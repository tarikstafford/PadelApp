import enum
from datetime import datetime, timedelta, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy import (
    Enum as SAEnum,
)
from sqlalchemy.orm import relationship

from app.database import Base


# Enum for game type
class GameType(str, enum.Enum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"
    # Add other types if needed, e.g., TOURNAMENT, LEAGUE


# Enum for game status
class GameStatus(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    club_id = Column(Integer, ForeignKey("clubs.id"), nullable=False, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), unique=True, nullable=False)
    team1_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    team2_id = Column(Integer, ForeignKey("teams.id"), nullable=True)

    # Game details
    game_type = Column(
        SAEnum(GameType, name="gametype", create_enum=False),
        default=GameType.PRIVATE,
        nullable=False,
    )
    game_status = Column(
        SAEnum(GameStatus, name="gamestatus", create_enum=False),
        default=GameStatus.SCHEDULED,
        nullable=False,
    )
    skill_level = Column(
        String, nullable=True
    )  # e.g., "Beginner", "Intermediate", "Advanced"

    # Timestamps inherited from booking for querying convenience
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)

    # Game result fields
    winning_team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    result_submitted = Column(Boolean, default=False, nullable=False)

    # Relationship to Club model
    club = relationship(
        "Club"
    )  # No back_populates needed if Club doesn't need to list games directly

    # Relationship to Booking model (one-to-one with Game)
    booking = relationship("Booking", back_populates="game")

    team1 = relationship("Team", foreign_keys=[team1_id])
    team2 = relationship("Team", foreign_keys=[team2_id])
    winning_team = relationship("Team", foreign_keys=[winning_team_id])

    # Relationship to User model (creator can be derived from booking.user_id)

    # Relationship to GamePlayer model (players participating in the game)
    players = relationship(
        "GamePlayer", back_populates="game", cascade="all, delete-orphan"
    )

    # Relationship to GameScore model (score submissions and confirmations)
    scores = relationship(
        "GameScore", back_populates="game", cascade="all, delete-orphan"
    )

    def is_expired(self) -> bool:
        """Check if the game is expired (past end time)"""
        current_time = datetime.now(timezone.utc)
        # Handle timezone-naive end_time
        if self.end_time.tzinfo is None:
            # Assume end_time is in UTC if no timezone info
            end_time_aware = self.end_time.replace(tzinfo=timezone.utc)
            return current_time > end_time_aware
        return current_time > self.end_time

    def can_leave_game(self) -> bool:
        """Check if players can leave (more than 24 hours before start)"""
        current_time = datetime.now(timezone.utc)
        # Handle timezone-naive start_time
        if self.start_time.tzinfo is None:
            # Assume start_time is in UTC if no timezone info
            start_time_aware = self.start_time.replace(tzinfo=timezone.utc)
            return current_time < (start_time_aware - timedelta(hours=24))
        return current_time < (self.start_time - timedelta(hours=24))

    def should_auto_expire(self) -> bool:
        """Check if game should be automatically expired"""
        return self.is_expired() and self.game_status == GameStatus.SCHEDULED

    def __repr__(self):
        return (
            f"<Game(id={self.id}, booking_id={self.booking_id}, "
            f"type='{self.game_type}', status='{self.game_status}')>"
        )
