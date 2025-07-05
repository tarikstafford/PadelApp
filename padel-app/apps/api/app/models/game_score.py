import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Text,
)
from sqlalchemy import (
    Enum as SAEnum,
)
from sqlalchemy.orm import relationship

from app.database import Base


class ScoreStatus(str, enum.Enum):
    PENDING = "PENDING"  # Score submitted, waiting for confirmation
    CONFIRMED = "CONFIRMED"  # Score confirmed by both teams
    DISPUTED = "DISPUTED"  # Score disputed by opposing team
    RESOLVED = "RESOLVED"  # Dispute resolved, final score set


class ConfirmationAction(str, enum.Enum):
    CONFIRM = "CONFIRM"  # Confirming the submitted score
    COUNTER = "COUNTER"  # Disputing and providing counter score


class GameScore(Base):
    __tablename__ = "game_scores"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False, index=True)

    # Score details
    team1_score = Column(Integer, nullable=False)
    team2_score = Column(Integer, nullable=False)

    # Submission details
    submitted_by_team = Column(Integer, nullable=False)  # 1 for team1, 2 for team2
    submitted_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Status tracking
    status = Column(
        SAEnum(ScoreStatus, name="scorestatus", create_enum=False),
        default=ScoreStatus.PENDING,
        nullable=False,
    )

    # Final confirmed score (may differ from original if disputed)
    final_team1_score = Column(Integer, nullable=True)
    final_team2_score = Column(Integer, nullable=True)
    confirmed_at = Column(DateTime, nullable=True)

    # Admin resolution (if needed)
    admin_resolved = Column(Boolean, default=False, nullable=False)
    admin_notes = Column(Text, nullable=True)

    # Relationships
    game = relationship("Game", back_populates="scores")
    submitted_by = relationship("User", foreign_keys=[submitted_by_user_id])
    confirmations = relationship(
        "ScoreConfirmation", back_populates="game_score", cascade="all, delete-orphan"
    )

    def get_winning_team(self) -> int:
        """Get winning team number (1 or 2) based on final or current score"""
        team1_score = self.final_team1_score or self.team1_score
        team2_score = self.final_team2_score or self.team2_score

        if team1_score > team2_score:
            return 1
        if team2_score > team1_score:
            return 2
        return 0  # Tie (shouldn't happen in padel)

    def is_confirmed(self) -> bool:
        """Check if score is confirmed by both teams"""
        return self.status == ScoreStatus.CONFIRMED

    def __repr__(self):
        return f"<GameScore(id={self.id}, game_id={self.game_id}, score={self.team1_score}-{self.team2_score}, status='{self.status}')>"


class ScoreConfirmation(Base):
    __tablename__ = "score_confirmations"

    id = Column(Integer, primary_key=True, index=True)
    game_score_id = Column(
        Integer, ForeignKey("game_scores.id"), nullable=False, index=True
    )

    # Confirmation details
    confirming_team = Column(Integer, nullable=False)  # 1 for team1, 2 for team2
    confirming_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(
        SAEnum(ConfirmationAction, name="confirmationaction", create_enum=False),
        nullable=False,
    )
    confirmed_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Counter score (if action is COUNTER)
    counter_team1_score = Column(Integer, nullable=True)
    counter_team2_score = Column(Integer, nullable=True)
    counter_notes = Column(Text, nullable=True)  # Reason for dispute

    # Relationships
    game_score = relationship("GameScore", back_populates="confirmations")
    confirming_user = relationship("User", foreign_keys=[confirming_user_id])

    def __repr__(self):
        return f"<ScoreConfirmation(id={self.id}, game_score_id={self.game_score_id}, action='{self.action}', team={self.confirming_team})>"
