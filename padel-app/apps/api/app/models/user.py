from sqlalchemy import Column, Integer, String, Boolean, Enum
from sqlalchemy.orm import relationship

from app.database import Base
from .user_role import UserRole # Import the new enum

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    profile_picture_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    
    # New role field
    role = Column(Enum(UserRole), nullable=False, default=UserRole.PLAYER, server_default=UserRole.PLAYER.value)

    # Relationship to Bookings (one-to-many)
    bookings = relationship("Booking", back_populates="user")
    
    # Relationship to GamePlayer entries (one-to-many)
    games = relationship("GamePlayer", back_populates="player")

    # New relationship to Club (one-to-one)
    owned_club = relationship("Club", back_populates="owner", uselist=False, cascade="all, delete-orphan")

    # Optional: If we want a direct list of games created by the user,
    # (assuming a creator_id is added to the Game model or derived differently)
    # created_games = relationship("Game", foreign_keys="[Game.creator_id]", back_populates="creator")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', name='{self.name}')>" 