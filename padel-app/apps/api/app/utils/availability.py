from datetime import datetime, timedelta
from typing import Iterator, Tuple

def get_time_slots(start_time: datetime, end_time: datetime, duration_minutes: int) -> Iterator[Tuple[datetime, datetime]]:
    """
    Generates time slots of a specific duration between a start and end time.

    Args:
        start_time: The starting datetime of the period.
        end_time: The ending datetime of the period.
        duration_minutes: The duration of each time slot in minutes.

    Yields:
        A tuple containing the start and end datetime of each slot.
    """
    current_time = start_time
    slot_duration = timedelta(minutes=duration_minutes)

    while current_time + slot_duration <= end_time:
        slot_end_time = current_time + slot_duration
        yield current_time, slot_end_time
        current_time = slot_end_time 