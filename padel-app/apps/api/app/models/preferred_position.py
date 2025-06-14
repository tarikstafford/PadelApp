import enum

from sqlalchemy import Enum

class PreferredPosition(str, enum.Enum):
    LEFT = "LEFT"
    RIGHT = "RIGHT" 