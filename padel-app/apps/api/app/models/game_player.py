import enum

from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from app.database import Base


# Enum for GamePlayer status
class GamePlayerStatus(str, enum.Enum):
    INVITED = "INVITED"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    REQUESTED_TO_JOIN = "REQUESTED_TO_JOIN"  # New status for join requests
    # Add other statuses if needed, e.g., WAITING_LIST


class GamePlayer(Base):
    __tablename__ = "game_players"

    game_id = Column(Integer, ForeignKey("games.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    status = Column(
        SAEnum(GamePlayerStatus), nullable=False, default=GamePlayerStatus.INVITED
    )

    # Relationship to Game model
    game = relationship("Game", back_populates="players")

    # Relationship to User model
    user = relationship("User", back_populates="games")

    def __repr__(self):
        return f"<GamePlayer(game_id={self.game_id}, user_id={self.user_id}, status='{self.status.value}')>"
