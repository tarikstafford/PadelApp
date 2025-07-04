import datetime

from sqlalchemy.orm import Session

from app import crud
from app.schemas.court_schemas import (
    AvailabilityResponse,
    BookingTimeSlot,
    CalendarTimeSlot,
    DailyAvailability,
)
from app.utils.availability import get_time_slots

# Define default operating hours for slot generation (can be made dynamic later)
DEFAULT_OPENING_TIME = datetime.time(9, 0)  # 9:00 AM
DEFAULT_CLOSING_TIME = datetime.time(
    22, 0
)  # 10:00 PM (slots up to 21:30 will be generated)


def get_court_availability_for_day(
    db: Session, *, court_id: int, target_date: datetime.date, duration: int = 90
) -> list[BookingTimeSlot]:
    """
    Get the availability of a court for a single day.
    """
    db_court = crud.court_crud.get_court(db, court_id=court_id)
    if not db_court:
        return []

    opening_time = db_court.club.opening_time or DEFAULT_OPENING_TIME
    closing_time = db_court.club.closing_time or DEFAULT_CLOSING_TIME

    bookings_for_day = crud.booking_crud.get_bookings_for_court_on_date(
        db, court_id=court_id, target_date=target_date
    )
    booked_start_times = {b.start_time.time() for b in bookings_for_day}

    all_slots: list[BookingTimeSlot] = []

    now = datetime.datetime.now()

    for slot_start_time, slot_end_time in get_time_slots(
        opening_time, closing_time, duration
    ):
        slot_start_datetime = datetime.datetime.combine(target_date, slot_start_time)

        is_booked = slot_start_time in booked_start_times

        is_in_past = slot_start_datetime < now

        # A slot is available if it's not booked and not in the past.
        is_available = not is_booked and not is_in_past

        all_slots.append(
            BookingTimeSlot(
                start_time=slot_start_datetime.isoformat(),
                end_time=datetime.datetime.combine(
                    target_date, slot_end_time
                ).isoformat(),
                is_available=is_available,
            )
        )
    return all_slots


async def get_court_availability_for_range(
    db: Session, *, court_id: int, start_date: datetime.date, end_date: datetime.date
) -> AvailabilityResponse:
    """
    Get the availability of a court for a given date range.
    """
    db_court = crud.court_crud.get_court(db, court_id=court_id)
    if not db_court:
        # Or raise HTTPException(status_code=404, detail="Court not found")
        return AvailabilityResponse(days=[])

    # Fallback to defaults if club-specific times are not set
    opening_time = db_court.club.opening_time or DEFAULT_OPENING_TIME
    closing_time = db_court.club.closing_time or DEFAULT_CLOSING_TIME
    slot_duration = 90  # This could also be a court/club setting

    availability_by_day: list[DailyAvailability] = []
    current_date = start_date
    while current_date <= end_date:
        bookings_for_day = crud.booking_crud.get_bookings_for_court_on_date(
            db, court_id=court_id, target_date=current_date
        )
        booked_start_times = {b.start_time.time() for b in bookings_for_day}

        all_slots: list[CalendarTimeSlot] = []
        for interval_start, _ in get_time_slots(
            opening_time, closing_time, slot_duration
        ):
            is_booked = interval_start in booked_start_times
            all_slots.append(
                CalendarTimeSlot(
                    time=interval_start.strftime("%H:%M"), booked=is_booked
                )
            )

        availability_by_day.append(
            DailyAvailability(date=current_date, slots=all_slots)
        )
        current_date += datetime.timedelta(days=1)

    return AvailabilityResponse(days=availability_by_day)
