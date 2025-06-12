# This file makes 'routers' a Python package

from .auth import router as auth_router
from .admin import router as admin_router
from .clubs import router as clubs_router
from .courts import router as courts_router
from .bookings import router as bookings_router
from .games import router as games_router
from .users import router as users_router

# Import other routers here as they are created, e.g.:
# from .items import router as items_router

__all__ = [
    "auth_router", 
    "admin_router",
    "clubs_router", 
    "courts_router", 
    "bookings_router", 
    "games_router",
    "users_router",
] # Add other router names here 