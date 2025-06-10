from enum import Enum

class UserRole(str, Enum):
    PLAYER = "player"
    ADMIN = "admin"
    SUPER_ADMIN = "super-admin" 