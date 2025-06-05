from typing import List, Tuple
from sqlalchemy.orm import Session
from datetime import date, datetime, time, timedelta

from app import crud, schemas # For schemas.TimeSlot and crud.booking_crud
from app.models import Court # To potentially check court existence or specific court opening hours in future

# Define default operating hours for slot generation (can be made dynamic later)
DEFAULT_OPENING_TIME = time(8, 0)  # 8:00 AM
DEFAULT_CLOSING_TIME = time(22, 0) # 10:00 PM (slots up to 21:30 will be generated)
SLOT_INTERVAL_MINUTES = 30

def _generate_daily_time_slots(
    target_date: date, 
    opening_time: time = DEFAULT_OPENING_TIME, 
    closing_time: time = DEFAULT_CLOSING_TIME, 
    interval_minutes: int = SLOT_INTERVAL_MINUTES
) -> List[Tuple[datetime, datetime]]:
    """Generates all possible time slots for a given date within operating hours."""
    slots = []
    current_slot_start_dt = datetime.combine(target_date, opening_time)
    closing_dt = datetime.combine(target_date, closing_time)
    slot_delta = timedelta(minutes=interval_minutes)

    while current_slot_start_dt < closing_dt:
        slot_end_dt = current_slot_start_dt + slot_delta
        # Ensure the slot doesn't exceed the closing time
        if slot_end_dt <= closing_dt:
            slots.append((current_slot_start_dt, slot_end_dt))
        current_slot_start_dt += slot_delta
    return slots

def get_court_availability(
    db: Session, 
    court_id: int, 
    target_date: date
) -> List[schemas.TimeSlot]:
    """
    Calculates the availability of a court for a given date by checking against existing bookings.
    """
    # Optional: Fetch court to verify existence or use court-specific opening hours in future
    # court = crud.court_crud.get_court(db, court_id=court_id)
    # if not court:
    #     # Or raise HTTPException if preferred to handle in router
    #     return [] 

    potential_slots = _generate_daily_time_slots(target_date)
    booked_slots_models = crud.booking_crud.get_bookings_for_court_on_date(
        db, court_id=court_id, target_date=target_date
    )

    # Create a set of booked start times for efficient lookup
    # Assuming bookings are exactly on the 30-min marks and for the SLOT_INTERVAL_MINUTES duration.
    # More complex logic would be needed if bookings can have variable durations or start off-interval.
    booked_start_times = {booking.start_time for booking in booked_slots_models}

    availability_slots = []
    for start_dt, end_dt in potential_slots:
        is_available = start_dt not in booked_start_times
        availability_slots.append(
            schemas.TimeSlot(start_time=start_dt, end_time=end_dt, is_available=is_available)
        )
    
    return availability_slots 