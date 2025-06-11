from enum import Enum

class UserRole(str, Enum):
    PLAYER = "player"
    ADMIN = "admin"
    SUPER_ADMIN = "super-admin"
    CLUB_ADMIN = "club_admin" 