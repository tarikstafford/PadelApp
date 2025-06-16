from datetime import datetime, date, time, timedelta
from typing import Iterator, Tuple

def get_time_slots(start_time: time, end_time: time, duration_minutes: int) -> Iterator[Tuple[time, time]]:
    """
    Generates time slots of a specific duration between a start and end time.

    Args:
        start_time: The starting time of the period.
        end_time: The ending time of the period.
        duration_minutes: The duration of each time slot in minutes.

    Yields:
        A tuple containing the start and end time of each slot.
    """
    current_time_dt = datetime.combine(date.min, start_time)
    end_time_dt = datetime.combine(date.min, end_time)
    slot_duration = timedelta(minutes=duration_minutes)

    while current_time_dt + slot_duration <= end_time_dt:
        slot_end_time_dt = current_time_dt + slot_duration
        yield current_time_dt.time(), slot_end_time_dt.time()
        current_time_dt = slot_end_time_dt 