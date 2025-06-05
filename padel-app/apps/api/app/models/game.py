from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
import enum

from app.database import Base

# Enum for game type
class GameType(str, enum.Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    # Add other types if needed, e.g., TOURNAMENT, LEAGUE

class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), unique=True, nullable=False)
    game_type = Column(SAEnum(GameType), default=GameType.PRIVATE, nullable=False)
    skill_level = Column(String, nullable=True) # e.g., "Beginner", "Intermediate", "Advanced"
    # created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False) # User who initiated the game/booking

    # Relationship to Booking model (one-to-one with Game)
    booking = relationship("Booking", back_populates="game")
    
    # Relationship to User model (creator of the game - can be derived from booking.user_id or be explicit here)
    # creator = relationship("User", back_populates="created_games") # Add to User model later

    # Relationship to GamePlayer model (players participating in the game)
    players = relationship("GamePlayer", back_populates="game", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Game(id={self.id}, booking_id={self.booking_id}, type='{self.game_type}')>" 