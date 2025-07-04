# This file makes 'routers' a Python package

from app.routers import (
    admin,
    auth,
    bookings,
    clubs,
    courts,
    games,
    leaderboard,
    public,
    users,
)

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
    "admin_router",
    "auth_router",
    "bookings_router",
    "clubs_router",
    "courts_router",
    "games_router",
    "public_router",
    "users_router",
]  # Add other router names here
