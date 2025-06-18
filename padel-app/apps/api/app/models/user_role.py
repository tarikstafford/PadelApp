from enum import Enum

class UserRole(str, Enum):
    PLAYER = "PLAYER"
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"
    CLUB_ADMIN = "CLUB_ADMIN" 