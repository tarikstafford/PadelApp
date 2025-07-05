import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class GameInvitation(Base):
    __tablename__ = "game_invitations"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    token = Column(String, unique=True, nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    max_uses = Column(Integer, default=None)  # None = unlimited
    current_uses = Column(Integer, default=0)

    # Relationships
    game = relationship("Game")
    creator = relationship("User")

    @classmethod
    def generate_token(cls):
        """Generate a secure random token for invitations"""
        return secrets.token_urlsafe(32)

    @classmethod
    def create_invitation(
        cls,
        game_id: int,
        created_by: int,
        expires_in_hours: int = 24,
        max_uses: Optional[int] = None,
    ):
        """Create a new game invitation with default expiration"""
        return cls(
            game_id=game_id,
            token=cls.generate_token(),
            created_by=created_by,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=expires_in_hours),
            max_uses=max_uses,
        )

    def is_valid(self) -> bool:
        """Check if invitation is still valid"""
        if not self.is_active:
            return False

        if datetime.now(timezone.utc) > self.expires_at:
            return False

        return not (self.max_uses is not None and self.current_uses >= self.max_uses)

    def increment_usage(self):
        """Increment the usage counter"""
        self.current_uses += 1

    def __repr__(self):
        return (
            f"<GameInvitation(id={self.id}, game_id={self.game_id}, "
            f"token={self.token[:8]}...)>"
        )
