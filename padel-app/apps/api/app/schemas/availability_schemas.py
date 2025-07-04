from datetime import datetime

from pydantic import BaseModel


class TimeSlot(BaseModel):
    start_time: datetime
    end_time: datetime
    is_available: bool

    model_config = {
        "from_attributes": True
    }  # If ever created from an ORM model directly
