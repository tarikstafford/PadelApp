# This file makes 'routers' a Python package

from . import auth
from . import users
from . import clubs
from . import courts
from . import bookings
from . import games
from . import admin
from . import leaderboard
from . import public

auth_router = auth.router
users_router = users.router
clubs_router = clubs.router
courts_router = courts.router
bookings_router = bookings.router
games_router = games.router
admin_router = admin.router
leaderboard_router = leaderboard.router
public_router = public.router

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
    "public_router",
] # Add other router names here 