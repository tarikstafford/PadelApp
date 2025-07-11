from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.preferred_position import PreferredPosition
from app.models.team import team_players
from app.models.user_role import UserRole  # Import the new enum


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    profile_picture_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False, server_default="true")

    # New role field
    role = Column(
        SAEnum(UserRole, name="userrole"),
        nullable=False,
        default=UserRole.PLAYER,
        server_default=UserRole.PLAYER.value,
        index=True,
    )

    elo_rating = Column(Float, nullable=False, default=1.0, server_default="1.0")
    preferred_position = Column(
        SAEnum(PreferredPosition, name="preferredposition", create_enum=False),
        nullable=True,
    )
    
    # Onboarding fields
    onboarding_completed = Column(Boolean, default=False, nullable=False, server_default="false")
    onboarding_completed_at = Column(DateTime, nullable=True)
    
    # Privacy settings for game history
    is_game_history_public = Column(Boolean, default=True, nullable=False, server_default="true")
    is_game_statistics_public = Column(Boolean, default=True, nullable=False, server_default="true")

    # Relationship to Bookings (one-to-many)
    bookings = relationship("Booking", back_populates="user")

    # Relationship to GamePlayer entries (one-to-many)
    games = relationship("GamePlayer", back_populates="user")

    # New relationship to Club (one-to-one)
    owned_club = relationship(
        "Club", back_populates="owner", uselist=False, cascade="all, delete-orphan"
    )

    # Relationship to ClubAdmin entries
    club_admin_entries = relationship(
        "ClubAdmin", back_populates="user", cascade="all, delete-orphan"
    )


    is_superuser = Column(Boolean(), default=False)

    teams = relationship("Team", secondary=team_players, back_populates="players")
    
    # Relationship to team memberships
    team_memberships = relationship("TeamMembership", back_populates="user", cascade="all, delete-orphan")

    elo_adjustment_requests = relationship(
        "EloAdjustmentRequest", back_populates="user"
    )

    # Financial relationships
    payment_transactions = relationship(
        "PaymentTransaction", back_populates="user", cascade="all, delete-orphan"
    )
    club_memberships = relationship(
        "ClubMembership", back_populates="user", cascade="all, delete-orphan"
    )

    # Team membership relationships
    team_memberships = relationship(
        "TeamMembership", back_populates="user", cascade="all, delete-orphan"
    )

    # Notification relationships
    notifications = relationship(
        "Notification", back_populates="user", cascade="all, delete-orphan"
    )
    notification_preferences = relationship(
        "NotificationPreference",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', name='{self.full_name}')>"
