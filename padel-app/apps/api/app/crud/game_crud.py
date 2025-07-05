from datetime import date, datetime, time, timezone
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.booking import Booking as BookingModel
from app.models.court import Court as CourtModel
from app.models.game import Game as GameModel
from app.models.game import GameType
from app.models.game_player import GamePlayer as GamePlayerModel
from app.models.game_player import GamePlayerStatus
from app.schemas.game_schemas import GameCreate

MAX_PLAYERS_PER_GAME = 4


class GameCRUD:
    def create_game(
        self,
        db: Session,
        game_in: GameCreate,
        club_id: int,
        start_time: datetime,
        end_time: datetime,
    ) -> GameModel:
        """Create a new game linked to a booking."""
        db_game = GameModel(
            booking_id=game_in.booking_id,
            club_id=club_id,
            game_type=game_in.game_type,
            skill_level=game_in.skill_level,
            start_time=start_time,
            end_time=end_time,
        )
        db.add(db_game)
        db.commit()
        db.refresh(db_game)
        return db_game

    def get_game(self, db: Session, game_id: int) -> Optional[GameModel]:
        """
        Retrieve a single game by its ID, eager loading booking, players, and
        their user details.
        """
        return (
            db.query(GameModel)
            .filter(GameModel.id == game_id)
            .options(
                joinedload(GameModel.booking)
                .joinedload(BookingModel.court)
                .joinedload(CourtModel.club),
                joinedload(GameModel.players).joinedload(GamePlayerModel.user),
            )
            .first()
        )

    def get_game_with_teams(self, db: Session, game_id: int) -> Optional[GameModel]:
        """
        Retrieve a single game by its ID, eager loading teams and their players.
        """
        return (
            db.query(GameModel)
            .filter(GameModel.id == game_id)
            .options(
                joinedload(GameModel.team1).joinedload("players"),
                joinedload(GameModel.team2).joinedload("players"),
            )
            .first()
        )

    def get_public_games(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        target_date: Optional[date] = None,
        future_only: bool = True,
    ) -> list[GameModel]:
        """
        Retrieve a list of public games with available slots, optionally
        filtered by date. By default only shows future games.
        Eager loads necessary relationships for GameResponse.
        """
        subquery = (
            db.query(
                GamePlayerModel.game_id,
                func.count(GamePlayerModel.user_id).label("accepted_player_count"),
            )
            .filter(GamePlayerModel.status == GamePlayerStatus.ACCEPTED)
            .group_by(GamePlayerModel.game_id)
            .subquery()
        )

        query = (
            db.query(GameModel)
            .outerjoin(subquery, GameModel.id == subquery.c.game_id)
            .join(GameModel.booking)
            .filter(GameModel.game_type == GameType.PUBLIC)
            .filter(
                func.coalesce(subquery.c.accepted_player_count, 0)
                < MAX_PLAYERS_PER_GAME
            )
        )

        if target_date:
            start_datetime = datetime.combine(target_date, time.min)
            end_datetime = datetime.combine(target_date, time.max)
            query = query.filter(
                BookingModel.start_time >= start_datetime,
                BookingModel.start_time <= end_datetime,
            )

        # Filter for future games only (default behavior)
        if future_only:
            query = query.filter(BookingModel.start_time > datetime.now(timezone.utc))

        return (
            query.order_by(BookingModel.start_time)
            .offset(skip)
            .limit(limit)
            .options(
                joinedload(GameModel.booking)
                .joinedload(BookingModel.court)
                .joinedload(CourtModel.club),
                joinedload(GameModel.players).joinedload(GamePlayerModel.user),
            )
            .all()
        )

    def get_recent_games_by_club(
        self, db: Session, club_id: int, limit: int = 5
    ) -> list[GameModel]:
        """Get the most recent games for a specific club."""
        return (
            db.query(GameModel)
            .join(GameModel.booking)
            .join(BookingModel.court)
            .filter(CourtModel.club_id == club_id)
            .order_by(GameModel.created_at.desc())
            .limit(limit)
            .options(selectinload(GameModel.players).selectinload(GamePlayerModel.user))
            .all()
        )

    def get_game_by_booking(self, db: Session, booking_id: int) -> Optional[GameModel]:
        """Get a game by its booking ID."""
        return (
            db.query(GameModel)
            .filter(GameModel.booking_id == booking_id)
            .options(joinedload(GameModel.players).joinedload(GamePlayerModel.user))
            .first()
        )


# Create instance
game_crud = GameCRUD()
