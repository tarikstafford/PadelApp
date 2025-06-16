from sqlalchemy import Column, Integer, String, Boolean, Enum as SAEnum, Float
from sqlalchemy.orm import relationship
import enum

from app.database import Base
from .user_role import UserRole # Import the new enum
from .team import team_players
from .preferred_position import PreferredPosition
from .elo_adjustment_request import EloAdjustmentRequest

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    profile_picture_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False, server_default='true')
    
    # New role field
    role = Column(
        SAEnum(UserRole, name="userrole", create_enum=False, values_callable=lambda obj: [e.value for e in obj]), 
        nullable=False, 
        default=UserRole.PLAYER.value, 
        server_default=UserRole.PLAYER.value, 
        index=True
    )

    elo_rating = Column(Float, nullable=False, default=1.0, server_default="1.0")
    preferred_position = Column(SAEnum(PreferredPosition, name="preferredposition", create_enum=False), nullable=True)

    # Relationship to Bookings (one-to-many)
    bookings = relationship("Booking", back_populates="user")
    
    # Relationship to GamePlayer entries (one-to-many)
    games = relationship("GamePlayer", back_populates="user")

    # New relationship to Club (one-to-one)
    owned_club = relationship("Club", back_populates="owner", uselist=False, cascade="all, delete-orphan")

    # Relationship to ClubAdmin entries
    club_admin_entries = relationship("ClubAdmin", back_populates="user", cascade="all, delete-orphan")

    # Optional: If we want a direct list of games created by the user,
    # (assuming a creator_id is added to the Game model or derived differently)
    # created_games = relationship("Game", foreign_keys="[Game.creator_id]", back_populates="creator")

    is_superuser = Column(Boolean(), default=False)
    
    teams = relationship("Team", secondary=team_players, back_populates="players")

    elo_adjustment_requests = relationship("EloAdjustmentRequest", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', name='{self.full_name}')>" 