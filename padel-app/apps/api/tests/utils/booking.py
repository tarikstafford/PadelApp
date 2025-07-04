from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app import crud
from app.models.booking import Booking
from app.schemas.booking_schemas import BookingCreate


def create_random_booking(
    db: Session, court_id: int, user_id: int, start_time: Optional[datetime] = None
) -> Booking:
    if start_time is None:
        start_time = datetime.now(timezone.utc) + timedelta(hours=1)

    booking_in = BookingCreate(
        court_id=court_id,
        start_time=start_time,
        duration=90,  # Default duration for tests
    )
    return crud.booking_crud.create_booking(
        db=db, booking_in=booking_in, user_id=user_id
    )
