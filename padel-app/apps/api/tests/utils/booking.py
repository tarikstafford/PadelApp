from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app import crud
from app.schemas.booking_schemas import BookingCreate
from app.models.booking import Booking

def create_random_booking(db: Session, court_id: int, user_id: int, start_time: datetime = None) -> Booking:
    if start_time is None:
        start_time = datetime.utcnow() + timedelta(hours=1)
    
    booking_in = BookingCreate(
        court_id=court_id,
        start_time=start_time,
        duration=90  # Default duration for tests
    )
    return crud.booking_crud.create_booking(db=db, booking_in=booking_in, user_id=user_id) 