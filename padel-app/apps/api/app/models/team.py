from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from app.database import Base

team_players = Table(
    "team_players",
    Base.metadata,
    Column("team_id", Integer, ForeignKey("teams.id")),
    Column("user_id", Integer, ForeignKey("users.id")),
)


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    players = relationship("User", secondary=team_players, back_populates="teams")
    
    # Team statistics relationship
    stats = relationship("TeamStats", back_populates="team", uselist=False, cascade="all, delete-orphan")
    
    # Team game history
    game_history = relationship("TeamGameHistory", back_populates="team", cascade="all, delete-orphan")
