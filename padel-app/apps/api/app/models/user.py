from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    profile_picture_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    # Relationship to Bookings made by the user
    bookings = relationship("Booking", back_populates="user")
    
    # Relationship to Games the user is participating in (via GamePlayer)
    game_participations = relationship("GamePlayer", back_populates="player")

    # Optional: If we want a direct list of games created by the user,
    # (assuming a creator_id is added to the Game model or derived differently)
    # created_games = relationship("Game", foreign_keys="[Game.creator_id]", back_populates="creator")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', name='{self.name}')>" 