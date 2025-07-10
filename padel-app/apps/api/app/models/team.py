from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table
import sqlalchemy as sa
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
    description = Column(String, nullable=True)
    logo_url = Column(String, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP"))
    is_active = Column(Boolean, default=True, nullable=False, server_default="true")

    # Relationship to creator (User)
    creator = relationship("User", foreign_keys=[created_by])

    # Relationship to team memberships (replacing the old team_players relationship)
    team_memberships = relationship("TeamMembership", back_populates="team", cascade="all, delete-orphan")

    # Keep the old players relationship for backward compatibility if needed
    players = relationship("User", secondary=team_players, back_populates="teams")

    # Team statistics relationship
    stats = relationship(
        "TeamStats", back_populates="team", uselist=False, cascade="all, delete-orphan"
    )

    # Team game history
    game_history = relationship(
        "TeamGameHistory",
        foreign_keys="[TeamGameHistory.team_id]",
        back_populates="team",
        cascade="all, delete-orphan",
    )
