import pytest
from pydantic import ValidationError

from app.models.user import PreferredPosition  # Import the enum
from app.models.user_role import UserRole  # Import the UserRole enum
from app.schemas.game_schemas import (
    GameResultRequest,
    UserWithRating,
)


def test_game_result_request_valid():
    data = {"winning_team_id": 1}
    req = GameResultRequest(**data)
    assert req.winning_team_id == 1


def test_game_result_request_invalid():
    with pytest.raises(ValidationError):
        GameResultRequest()  # winning_team_id is required


def test_user_with_rating_valid():
    user_data = {
        "id": 1,
        "email": "test@example.com",
        "full_name": "Test User",
        "elo_rating": 5.5,
        "preferred_position": PreferredPosition.LEFT,
        "is_active": True,
        "is_superuser": False,
        "role": UserRole.PLAYER,
    }
    user = UserWithRating(**user_data)
    assert user.elo_rating == 5.5
    assert user.full_name == "Test User"
