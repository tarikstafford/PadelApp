from typing import Optional, List
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import func, and_
from datetime import date, datetime, time

from app.models.game import Game as GameModel, GameType
from app.models.game_player import GamePlayer as GamePlayerModel, GamePlayerStatus
from app.models.user import User as UserModel
from app.models.booking import Booking as BookingModel
from app.models.court import Court as CourtModel
from app.schemas.game_schemas import GameCreate

MAX_PLAYERS_PER_GAME = 4

def create_game(db: Session, game_in: GameCreate) -> GameModel:
    """Create a new game linked to a booking."""
    
    # Ensure game_type is lowercase before creating the model
    game_type_value = game_in.game_type.value if isinstance(game_in.game_type, GameType) else str(game_in.game_type).lower()

    db_game = GameModel(
        booking_id=game_in.booking_id,
        game_type=game_type_value,
        skill_level=game_in.skill_level
    )
    db.add(db_game)
    db.commit()
    db.refresh(db_game)
    return db_game

def get_game(db: Session, game_id: int) -> Optional[GameModel]:
    """
    Retrieve a single game by its ID, eager loading booking, players, and their user details.
    """
    return (
        db.query(GameModel)
        .filter(GameModel.id == game_id)
        .options(
            selectinload(GameModel.booking).selectinload(BookingModel.court).selectinload(CourtModel.club),
            selectinload(GameModel.players).selectinload(GamePlayerModel.player)
        )
        .first()
    )

def get_public_games(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    target_date: Optional[date] = None
) -> List[GameModel]:
    """
    Retrieve a list of public games with available slots, optionally filtered by date.
    Eager loads necessary relationships for GameResponse.
    """
    subquery = (
        db.query(
            GamePlayerModel.game_id,
            func.count(GamePlayerModel.id).label("accepted_player_count")
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
        .filter(func.coalesce(subquery.c.accepted_player_count, 0) < MAX_PLAYERS_PER_GAME)
    )

    if target_date:
        start_datetime = datetime.combine(target_date, time.min)
        end_datetime = datetime.combine(target_date, time.max)
        query = query.filter(
            BookingModel.start_time >= start_datetime,
            BookingModel.start_time <= end_datetime
        )
    
    games = (
        query
        .order_by(BookingModel.start_time)
        .offset(skip)
        .limit(limit)
        .options(
            selectinload(GameModel.booking).selectinload(BookingModel.court).selectinload(CourtModel.club),
            selectinload(GameModel.players).selectinload(GamePlayerModel.player)
        )
        .all()
    )
    return games

def get_recent_games_by_club(db: Session, club_id: int, limit: int = 5) -> List[GameModel]:
    """Get the most recent games for a specific club."""
    return (
        db.query(GameModel)
        .join(GameModel.booking)
        .join(BookingModel.court)
        .filter(CourtModel.club_id == club_id)
        .order_by(GameModel.created_at.desc())
        .limit(limit)
        .options(
            selectinload(GameModel.players).selectinload(GamePlayerModel.player)
        )
        .all()
    )

def get_game_by_booking(db: Session, booking_id: int) -> Optional[GameModel]:
    """Get a game by its booking ID."""
    return (
        db.query(GameModel)
        .filter(GameModel.booking_id == booking_id)
        .options(
            selectinload(GameModel.players).selectinload(GamePlayerModel.player)
        )
        .first()
    )

# Placeholder for other game CRUD operations if needed later
# def update_game(...)
# def delete_game(...) 