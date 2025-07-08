import enum
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy import (
    Enum as SAEnum,
)
from sqlalchemy.orm import relationship

from app.database import Base


class TournamentStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    REGISTRATION_OPEN = "REGISTRATION_OPEN"
    REGISTRATION_CLOSED = "REGISTRATION_CLOSED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class TournamentType(str, enum.Enum):
    SINGLE_ELIMINATION = "SINGLE_ELIMINATION"
    DOUBLE_ELIMINATION = "DOUBLE_ELIMINATION"
    AMERICANO = "AMERICANO"
    FIXED_AMERICANO = "FIXED_AMERICANO"


class TournamentCategory(str, enum.Enum):
    BRONZE = "BRONZE"
    SILVER = "SILVER"
    GOLD = "GOLD"
    PLATINUM = "PLATINUM"


class RecurrencePattern(str, enum.Enum):
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    CUSTOM = "CUSTOM"


# Map categories to ELO ranges
CATEGORY_ELO_RANGES = {
    TournamentCategory.BRONZE: (1.0, 2.0),
    TournamentCategory.SILVER: (2.0, 3.0),
    TournamentCategory.GOLD: (3.0, 5.0),
    TournamentCategory.PLATINUM: (5.0, 10.0),  # Using 10.0 instead of infinity for database compatibility
}


class RecurringTournament(Base):
    __tablename__ = "recurring_tournaments"

    id = Column(Integer, primary_key=True, index=True)
    club_id = Column(Integer, ForeignKey("clubs.id"), nullable=False, index=True)

    # Series information
    series_name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Recurrence pattern
    recurrence_pattern = Column(
        SAEnum(RecurrencePattern, name="recurrencepattern", create_enum=False),
        nullable=False,
    )

    # Recurrence configuration
    interval_value = Column(Integer, nullable=False, default=1)  # Every X weeks/months
    days_of_week = Column(JSON, nullable=True)  # For weekly: [1,3,5] for Mon, Wed, Fri
    day_of_month = Column(Integer, nullable=True)  # For monthly: 15 for 15th of month

    # Series dates
    series_start_date = Column(DateTime, nullable=False)
    series_end_date = Column(DateTime, nullable=True)  # Optional end date

    # Tournament template settings
    tournament_type = Column(
        SAEnum(TournamentType, name="tournamenttype", create_enum=False), nullable=False
    )
    duration_hours = Column(Integer, nullable=False, default=3)  # Default 3 hours
    registration_deadline_hours = Column(
        Integer, nullable=False, default=24
    )  # 24h before start

    # Tournament settings
    max_participants = Column(Integer, nullable=False)
    entry_fee = Column(Float, nullable=True, default=0.0)

    # Generation settings
    advance_generation_days = Column(
        Integer, nullable=False, default=30
    )  # Generate 30 days ahead
    auto_generation_enabled = Column(Boolean, default=True, nullable=False)

    # Series status
    is_active = Column(Boolean, default=True, nullable=False)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    club = relationship("Club")
    tournaments = relationship(
        "Tournament",
        back_populates="recurring_tournament",
        cascade="all, delete-orphan",
    )
    category_templates = relationship(
        "RecurringTournamentCategoryTemplate",
        back_populates="recurring_tournament",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return (
            f"<RecurringTournament(id={self.id}, series_name='{self.series_name}', "
            f"pattern='{self.recurrence_pattern}')>"
        )


class RecurringTournamentCategoryTemplate(Base):
    __tablename__ = "recurring_tournament_category_templates"

    id = Column(Integer, primary_key=True, index=True)
    recurring_tournament_id = Column(
        Integer, ForeignKey("recurring_tournaments.id"), nullable=False
    )
    category = Column(
        SAEnum(TournamentCategory, name="tournamentcategory", create_enum=False),
        nullable=False,
    )
    max_participants = Column(Integer, nullable=False)
    min_elo = Column(Float, nullable=False)
    max_elo = Column(Float, nullable=False)

    # Relationships
    recurring_tournament = relationship(
        "RecurringTournament", back_populates="category_templates"
    )

    def __repr__(self):
        return (
            f"<RecurringTournamentCategoryTemplate(id={self.id}, category='{self.category}', "
            f"elo_range={self.min_elo}-{self.max_elo})>"
        )


class Tournament(Base):
    __tablename__ = "tournaments"

    id = Column(Integer, primary_key=True, index=True)
    club_id = Column(Integer, ForeignKey("clubs.id"), nullable=False, index=True)
    recurring_tournament_id = Column(
        Integer, ForeignKey("recurring_tournaments.id"), nullable=True, index=True
    )
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    tournament_type = Column(
        SAEnum(TournamentType, name="tournamenttype", create_enum=False), nullable=False
    )

    # Tournament dates
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    registration_deadline = Column(DateTime, nullable=False)

    # Tournament status
    status = Column(
        SAEnum(TournamentStatus, name="tournamentstatus", create_enum=False),
        default=TournamentStatus.DRAFT,
        nullable=False,
    )

    # Tournament settings
    max_participants = Column(Integer, nullable=False)
    entry_fee = Column(Float, nullable=True, default=0.0)

    # Scheduling configuration
    auto_schedule_enabled = Column(Boolean, default=False, nullable=True)
    hourly_time_slots = Column(JSON, nullable=True)  # Store selected hourly time slots
    assigned_court_ids = Column(JSON, nullable=True)  # Store assigned court IDs
    schedule_generated = Column(Boolean, default=False, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    club = relationship("Club")
    recurring_tournament = relationship(
        "RecurringTournament", back_populates="tournaments"
    )
    categories = relationship(
        "TournamentCategoryConfig",
        back_populates="tournament",
        cascade="all, delete-orphan",
    )
    teams = relationship(
        "TournamentTeam", back_populates="tournament", cascade="all, delete-orphan"
    )
    participants = relationship(
        "TournamentParticipant",
        back_populates="tournament",
        cascade="all, delete-orphan",
        lazy="select",
    )
    matches = relationship(
        "TournamentMatch", back_populates="tournament", cascade="all, delete-orphan"
    )
    court_bookings = relationship(
        "TournamentCourtBooking",
        back_populates="tournament",
        cascade="all, delete-orphan",
    )
    payment_transactions = relationship(
        "PaymentTransaction", back_populates="tournament", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return (
            f"<Tournament(id={self.id}, name='{self.name}', "
            f"type='{self.tournament_type}')>"
        )


class TournamentCategoryConfig(Base):
    __tablename__ = "tournament_category_configs"

    id = Column(Integer, primary_key=True, index=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.id"), nullable=False)
    category = Column(
        SAEnum(TournamentCategory, name="tournamentcategory", create_enum=False),
        nullable=False,
    )
    max_participants = Column(Integer, nullable=False)
    min_elo = Column(Float, nullable=False)
    max_elo = Column(Float, nullable=False)

    # Relationships
    tournament = relationship("Tournament", back_populates="categories")
    teams = relationship(
        "TournamentTeam", back_populates="category_config", cascade="all, delete-orphan"
    )
    participants = relationship(
        "TournamentParticipant",
        back_populates="category_config",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self):
        return (
            f"<TournamentCategoryConfig(id={self.id}, category='{self.category}', "
            f"elo_range={self.min_elo}-{self.max_elo})>"
        )


class TournamentParticipant(Base):
    __tablename__ = "tournament_participants"

    id = Column(Integer, primary_key=True, index=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.id"), nullable=False)
    category_config_id = Column(
        Integer, ForeignKey("tournament_category_configs.id"), nullable=False
    )
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Participant-specific data
    seed_position = Column(Integer, nullable=True)  # Seeding position for Americano
    elo_at_registration = Column(Float, nullable=False)  # User's ELO at registration
    registration_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # For Americano tournaments - track which temporary teams they're part of
    match_teams = Column(
        JSON, nullable=True
    )  # Store temporary team assignments per round

    # Relationships
    tournament = relationship("Tournament", back_populates="participants")
    category_config = relationship(
        "TournamentCategoryConfig", back_populates="participants"
    )
    user = relationship("User", foreign_keys=[user_id])

    def __repr__(self):
        return (
            f"<TournamentParticipant(id={self.id}, tournament_id={self.tournament_id}, "
            f"user_id={self.user_id}, seed={self.seed})>"
        )


class TournamentTeam(Base):
    __tablename__ = "tournament_teams"

    id = Column(Integer, primary_key=True, index=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.id"), nullable=False)
    category_config_id = Column(
        Integer, ForeignKey("tournament_category_configs.id"), nullable=False
    )
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)

    # Tournament-specific data
    seed = Column(Integer, nullable=True)  # Seeding position in bracket
    average_elo = Column(Float, nullable=False)  # Team's average ELO at registration
    registration_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    tournament = relationship("Tournament", back_populates="teams")
    category_config = relationship("TournamentCategoryConfig", back_populates="teams")
    team = relationship("Team")

    # Tournament matches as team1 or team2
    matches_as_team1 = relationship(
        "TournamentMatch",
        foreign_keys="[TournamentMatch.team1_id]",
        back_populates="team1",
    )
    matches_as_team2 = relationship(
        "TournamentMatch",
        foreign_keys="[TournamentMatch.team2_id]",
        back_populates="team2",
    )

    def __repr__(self):
        return (
            f"<TournamentTeam(id={self.id}, tournament_id={self.tournament_id}, "
            f"team_id={self.team_id}, seed={self.seed})>"
        )


class MatchStatus(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    WALKOVER = "WALKOVER"


class TournamentMatch(Base):
    __tablename__ = "tournament_matches"

    id = Column(Integer, primary_key=True, index=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.id"), nullable=False)
    category_config_id = Column(
        Integer, ForeignKey("tournament_category_configs.id"), nullable=False
    )

    # Teams playing
    team1_id = Column(Integer, ForeignKey("tournament_teams.id"), nullable=True)
    team2_id = Column(Integer, ForeignKey("tournament_teams.id"), nullable=True)

    # Match details
    round_number = Column(
        Integer, nullable=False
    )  # 1 for first round, 2 for second, etc.
    match_number = Column(Integer, nullable=False)  # Match number within the round

    # Scheduling
    scheduled_time = Column(DateTime, nullable=True)
    court_id = Column(Integer, ForeignKey("courts.id"), nullable=True)

    # Results
    status = Column(
        SAEnum(MatchStatus, name="matchstatus", create_enum=False),
        default=MatchStatus.SCHEDULED,
        nullable=False,
    )
    winning_team_id = Column(Integer, ForeignKey("tournament_teams.id"), nullable=True)
    team1_score = Column(Integer, nullable=True)
    team2_score = Column(Integer, nullable=True)

    # Game reference (if match is played through regular game system)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=True)

    # Bracket progression
    winner_advances_to_match_id = Column(
        Integer, ForeignKey("tournament_matches.id"), nullable=True
    )
    loser_advances_to_match_id = Column(
        Integer, ForeignKey("tournament_matches.id"), nullable=True
    )  # For double elimination

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    tournament = relationship("Tournament", back_populates="matches")
    category_config = relationship("TournamentCategoryConfig")
    team1 = relationship(
        "TournamentTeam", foreign_keys=[team1_id], back_populates="matches_as_team1"
    )
    team2 = relationship(
        "TournamentTeam", foreign_keys=[team2_id], back_populates="matches_as_team2"
    )
    winning_team = relationship("TournamentTeam", foreign_keys=[winning_team_id])
    court = relationship("Court")
    game = relationship("Game")

    # Self-referential relationships for bracket progression
    winner_advances_to = relationship(
        "TournamentMatch", remote_side=[id], foreign_keys=[winner_advances_to_match_id]
    )
    loser_advances_to = relationship(
        "TournamentMatch", remote_side=[id], foreign_keys=[loser_advances_to_match_id]
    )

    def __repr__(self):
        return (
            f"<TournamentMatch(id={self.id}, tournament_id={self.tournament_id}, "
            f"round={self.round_number}, match={self.match_number})>"
        )


class TournamentCourtBooking(Base):
    __tablename__ = "tournament_court_bookings"

    id = Column(Integer, primary_key=True, index=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.id"), nullable=False)
    court_id = Column(Integer, ForeignKey("courts.id"), nullable=False)

    # Time slots blocked for tournament
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)

    # Whether this booking is currently in use by a match
    is_occupied = Column(Boolean, default=False, nullable=False)
    match_id = Column(Integer, ForeignKey("tournament_matches.id"), nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    tournament = relationship("Tournament", back_populates="court_bookings")
    court = relationship("Court")
    match = relationship("TournamentMatch")

    def __repr__(self):
        return (
            f"<TournamentCourtBooking(id={self.id}, "
            f"tournament_id={self.tournament_id}, court_id={self.court_id})>"
        )


class TournamentTrophy(Base):
    __tablename__ = "tournament_trophies"

    id = Column(Integer, primary_key=True, index=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.id"), nullable=False)
    category_config_id = Column(
        Integer, ForeignKey("tournament_category_configs.id"), nullable=False
    )
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)

    # Trophy details
    position = Column(Integer, nullable=False)  # 1 for winner, 2 for runner-up, etc.
    trophy_type = Column(
        String, nullable=False
    )  # "WINNER", "RUNNER_UP", "SEMI_FINALIST"

    # Metadata
    awarded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    tournament = relationship("Tournament")
    category_config = relationship("TournamentCategoryConfig")
    user = relationship("User")
    team = relationship("Team")

    def __repr__(self):
        return (
            f"<TournamentTrophy(id={self.id}, tournament_id={self.tournament_id}, "
            f"user_id={self.user_id}, position={self.position})>"
        )
