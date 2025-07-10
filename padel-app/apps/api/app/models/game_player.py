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


# Enum for GamePlayer position
class GamePlayerPosition(str, enum.Enum):
    LEFT = "LEFT"
    RIGHT = "RIGHT"


# Enum for GamePlayer team side
class GamePlayerTeamSide(str, enum.Enum):
    TEAM_1 = "TEAM_1"
    TEAM_2 = "TEAM_2"


class GamePlayer(Base):
    __tablename__ = "game_players"

    game_id = Column(Integer, ForeignKey("games.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    status = Column(
        SAEnum(GamePlayerStatus), nullable=False, default=GamePlayerStatus.INVITED
    )
    position = Column(
        SAEnum(GamePlayerPosition, name="gameplayerposition"),
        nullable=True,
    )
    team_side = Column(
        SAEnum(GamePlayerTeamSide, name="gameplayerteamside"),
        nullable=True,
    )

    # Relationship to Game model
    game = relationship("Game", back_populates="players")

    # Relationship to User model
    user = relationship("User", back_populates="games")

    def __repr__(self):
        return (
            f"<GamePlayer(game_id={self.game_id}, user_id={self.user_id}, "
            f"status='{self.status.value}', position='{self.position.value if self.position else None}', "
            f"team_side='{self.team_side.value if self.team_side else None}')>"
        )
