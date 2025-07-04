# This file makes 'crud' a Python package

# Import function-based CRUD modules
from app.crud import (
    booking_crud,
    club_admin_crud,
    club_crud,
    court_crud,
    elo_adjustment_request_crud,
    leaderboard_crud,
    user_crud,
)

# Import class-based CRUD instances
from app.crud.game_crud import game_crud
from app.crud.game_invitation_crud import game_invitation_crud
from app.crud.game_player_crud import game_player_crud
from app.crud.team_crud import team_crud
from app.crud.tournament_crud import tournament_crud

__all__ = [
    "booking_crud",
    "club_admin_crud",
    "club_crud",
    "court_crud",
    "elo_adjustment_request_crud",
    "game_crud",
    "game_invitation_crud",
    "game_player_crud",
    "leaderboard_crud",
    "team_crud",
    "tournament_crud",
    "user_crud",
]
