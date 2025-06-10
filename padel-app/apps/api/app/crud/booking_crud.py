from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, desc, asc
from datetime import date, datetime, time, timedelta

from app.models.booking import Booking as BookingModel, BookingStatus
from app.models.court import Court as CourtModel
from app.schemas.booking_schemas import BookingCreate
# from app.schemas.booking_schemas import BookingUpdate # For future C/U operations

# Import SLOT_INTERVAL_MINUTES, ideally from a shared config or constants file
# For now, let's assume it's accessible or define it locally if needed for CRUD clarity.
# from app.services.availability_service import SLOT_INTERVAL_MINUTES # Or define/import from elsewhere
SLOT_INTERVAL_MINUTES = 30 # Defining locally for now, can be refactored

def get_bookings_for_court_on_date(
    db: Session, 
    court_id: int, 
    target_date: date
) -> List[BookingModel]:
    """Retrieve all bookings for a specific court on a given date."""
    # Define the start and end of the target_date
    start_datetime = datetime.combine(target_date, time.min)
    end_datetime = datetime.combine(target_date, time.max)

    return (
        db.query(BookingModel)
        .filter(
            BookingModel.court_id == court_id,
            BookingModel.start_time >= start_datetime,
            BookingModel.start_time <= end_datetime
            # Could also filter by BookingModel.status if only confirmed bookings block slots
        )
        .all()
    )

def create_booking(db: Session, booking_in: BookingCreate, user_id: int) -> BookingModel:
    """Create a new booking in the database."""
    end_time = booking_in.start_time + timedelta(minutes=SLOT_INTERVAL_MINUTES)
    
    db_booking = BookingModel(
        court_id=booking_in.court_id,
        user_id=user_id,
        start_time=booking_in.start_time,
        end_time=end_time,
        status=BookingStatus.CONFIRMED
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)

    # Re-fetch the booking with relationships loaded to return the full object
    return (
        db.query(BookingModel)
        .options(
            joinedload(BookingModel.user),
            joinedload(BookingModel.court)
        )
        .filter(BookingModel.id == db_booking.id)
        .first()
    )

def get_booking(db: Session, booking_id: int) -> Optional[BookingModel]:
    """Retrieve a single booking by its ID."""
    return db.query(BookingModel).filter(BookingModel.id == booking_id).first()

def get_bookings_by_user(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    start_date_filter: Optional[date] = None,
    end_date_filter: Optional[date] = None,
    sort_by: Optional[str] = None, # e.g., "start_time", "status"
    sort_desc: bool = False
) -> List[BookingModel]:
    """Retrieve bookings for a specific user with pagination, date filtering, and sorting."""
    query = db.query(BookingModel).filter(BookingModel.user_id == user_id)
    query = query.options(joinedload(BookingModel.court))

    if start_date_filter:
        start_datetime_filter = datetime.combine(start_date_filter, time.min)
        query = query.filter(BookingModel.start_time >= start_datetime_filter)
    
    if end_date_filter:
        end_datetime_filter = datetime.combine(end_date_filter, time.max)
        query = query.filter(BookingModel.start_time <= end_datetime_filter)

    if sort_by:
        column_to_sort = getattr(BookingModel, sort_by, None)
        if column_to_sort is not None:
            if sort_desc:
                query = query.order_by(desc(column_to_sort))
            else:
                query = query.order_by(asc(column_to_sort))
        else:
            query = query.order_by(desc(BookingModel.start_time)) # Default sort by start_time desc if invalid sort_by
    else:
        query = query.order_by(desc(BookingModel.start_time)) # Default sort by start_time descending
    
    return query.offset(skip).limit(limit).all()

def get_bookings_by_club(
    db: Session,
    club_id: int,
    skip: int = 0,
    limit: int = 100,
    start_date_filter: Optional[date] = None,
    end_date_filter: Optional[date] = None,
    court_id_filter: Optional[int] = None,
    status_filter: Optional[BookingStatus] = None,
    sort_by: Optional[str] = "start_time",
    sort_desc: bool = True
) -> List[BookingModel]:
    """Retrieve bookings for a specific club with pagination, filtering, and sorting."""
    query = (
        db.query(BookingModel)
        .join(CourtModel)
        .filter(CourtModel.club_id == club_id)
        .options(
            joinedload(BookingModel.user), 
            joinedload(BookingModel.court)
        )
    )

    if start_date_filter:
        start_datetime_filter = datetime.combine(start_date_filter, time.min)
        query = query.filter(BookingModel.start_time >= start_datetime_filter)
    
    if end_date_filter:
        end_datetime_filter = datetime.combine(end_date_filter, time.max)
        query = query.filter(BookingModel.start_time <= end_datetime_filter)
        
    if court_id_filter:
        query = query.filter(BookingModel.court_id == court_id_filter)
        
    if status_filter:
        query = query.filter(BookingModel.status == status_filter)

    if sort_by:
        column_to_sort = getattr(BookingModel, sort_by, None)
        if column_to_sort is not None:
            if sort_desc:
                query = query.order_by(desc(column_to_sort))
            else:
                query = query.order_by(asc(column_to_sort))
        else:
            query = query.order_by(desc(BookingModel.start_time))
    else:
        query = query.order_by(desc(BookingModel.start_time))
    
    return query.offset(skip).limit(limit).all()

def get_bookings_by_club_and_date(db: Session, club_id: int, target_date: date) -> List[BookingModel]:
    """Get all bookings for a specific club on a given date."""
    start_datetime = datetime.combine(target_date, time.min)
    end_datetime = datetime.combine(target_date, time.max)
    
    return (
        db.query(BookingModel)
        .join(CourtModel)
        .filter(
            CourtModel.club_id == club_id,
            BookingModel.start_time >= start_datetime,
            BookingModel.start_time <= end_datetime
        )
        .all()
    )

# Placeholder for get_booking
# def get_booking(db: Session, booking_id: int) -> Optional[BookingModel]:
#     ... 