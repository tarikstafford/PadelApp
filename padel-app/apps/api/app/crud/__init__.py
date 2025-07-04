# This file makes 'crud' a Python package

from app.crud import (
    booking_crud,
    club_admin_crud,
    club_crud,
    court_crud,
    elo_adjustment_request_crud,
    game_crud,
    game_player_crud,
    leaderboard_crud,
    team_crud,
    user_crud,
)

# Import other CRUD modules here as they are created

__all__ = [
    "booking_crud",
    "club_admin_crud",
    "club_crud",
    "court_crud",
    "elo_adjustment_request_crud",
    "game_crud",
    "game_player_crud",
    "leaderboard_crud",
    "team_crud",
    "user_crud",
]
