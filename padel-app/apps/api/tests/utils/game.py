from sqlalchemy.orm import Session
from app import crud
from app.schemas.game_schemas import GameCreate
from app.models.game import Game, GameType
from app.models.booking import Booking as BookingModel

def create_random_game(db: Session, booking: BookingModel, game_type: str = "PRIVATE") -> Game:
    game_in = GameCreate(
        booking_id=booking.id,
        game_type=GameType(game_type)
    )
    return crud.game_crud.create_game(
        db=db, 
        game_in=game_in, 
        club_id=booking.court.club_id, 
        start_time=booking.start_time, 
        end_time=booking.end_time
    ) 