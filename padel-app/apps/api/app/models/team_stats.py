from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
)
from sqlalchemy.orm import relationship

from app.database import Base


class TeamStats(Base):
    __tablename__ = "team_stats"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(
        Integer, ForeignKey("teams.id"), nullable=False, unique=True, index=True
    )

    # Game statistics
    games_played = Column(Integer, default=0, nullable=False)
    games_won = Column(Integer, default=0, nullable=False)
    games_lost = Column(Integer, default=0, nullable=False)

    # Score statistics
    total_points_scored = Column(Integer, default=0, nullable=False)
    total_points_conceded = Column(Integer, default=0, nullable=False)

    # ELO and performance
    current_average_elo = Column(Float, nullable=True)
    peak_average_elo = Column(Float, nullable=True)
    lowest_average_elo = Column(Float, nullable=True)

    # Tournament statistics
    tournaments_participated = Column(Integer, default=0, nullable=False)
    tournaments_won = Column(Integer, default=0, nullable=False)
    tournament_matches_won = Column(Integer, default=0, nullable=False)
    tournament_matches_lost = Column(Integer, default=0, nullable=False)

    # Streaks
    current_win_streak = Column(Integer, default=0, nullable=False)
    current_loss_streak = Column(Integer, default=0, nullable=False)
    longest_win_streak = Column(Integer, default=0, nullable=False)
    longest_loss_streak = Column(Integer, default=0, nullable=False)

    # Last activity
    last_game_date = Column(DateTime, nullable=True)
    last_updated = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    team = relationship("Team", back_populates="stats")

    @property
    def win_rate(self) -> float:
        """Calculate win rate percentage"""
        if self.games_played == 0:
            return 0.0
        return (self.games_won / self.games_played) * 100

    @property
    def points_per_game(self) -> float:
        """Calculate average points scored per game"""
        if self.games_played == 0:
            return 0.0
        return self.total_points_scored / self.games_played

    @property
    def points_conceded_per_game(self) -> float:
        """Calculate average points conceded per game"""
        if self.games_played == 0:
            return 0.0
        return self.total_points_conceded / self.games_played

    @property
    def point_differential(self) -> int:
        """Calculate total point differential (scored - conceded)"""
        return self.total_points_scored - self.total_points_conceded

    @property
    def tournament_win_rate(self) -> float:
        """Calculate tournament win rate percentage"""
        if self.tournaments_participated == 0:
            return 0.0
        return (self.tournaments_won / self.tournaments_participated) * 100

    def update_after_game(
        self, won: bool, points_scored: int, points_conceded: int, game_date: datetime
    ):
        """Update stats after a game"""
        self.games_played += 1
        self.total_points_scored += points_scored
        self.total_points_conceded += points_conceded
        self.last_game_date = game_date

        if won:
            self.games_won += 1
            self.current_win_streak += 1
            self.current_loss_streak = 0
            self.longest_win_streak = max(
                self.longest_win_streak, self.current_win_streak
            )
        else:
            self.games_lost += 1
            self.current_loss_streak += 1
            self.current_win_streak = 0
            self.longest_loss_streak = max(
                self.longest_loss_streak, self.current_loss_streak
            )

    def update_elo(self, new_average_elo: float):
        """Update ELO statistics"""
        self.current_average_elo = new_average_elo

        if self.peak_average_elo is None or new_average_elo > self.peak_average_elo:
            self.peak_average_elo = new_average_elo

        if self.lowest_average_elo is None or new_average_elo < self.lowest_average_elo:
            self.lowest_average_elo = new_average_elo

    def __repr__(self):
        return f"<TeamStats(id={self.id}, team_id={self.team_id}, games_played={self.games_played}, win_rate={self.win_rate:.1f}%)>"


class TeamGameHistory(Base):
    __tablename__ = "team_game_history"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False, index=True)

    # Game outcome for this team
    won = Column(Integer, nullable=False)  # 1 if won, 0 if lost
    points_scored = Column(Integer, nullable=False)
    points_conceded = Column(Integer, nullable=False)

    # Opponent info
    opponent_team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)

    # ELO changes
    elo_before = Column(Float, nullable=True)
    elo_after = Column(Float, nullable=True)
    elo_change = Column(Float, nullable=True)

    # Game context
    game_date = Column(DateTime, nullable=False)
    is_tournament_game = Column(
        Integer, default=0, nullable=False
    )  # 1 if tournament, 0 if regular
    tournament_id = Column(Integer, ForeignKey("tournaments.id"), nullable=True)

    # Timestamps
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    team = relationship("Team", foreign_keys=[team_id])
    game = relationship("Game")
    opponent_team = relationship("Team", foreign_keys=[opponent_team_id])
    tournament = relationship("Tournament")

    def __repr__(self):
        return f"<TeamGameHistory(id={self.id}, team_id={self.team_id}, game_id={self.game_id}, won={bool(self.won)})>"
