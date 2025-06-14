import pytest
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.core.config import settings
from app.crud.user_crud import get_user_by_email
from app import models

# The client and db_session fixtures are now autoused from conftest.py

@pytest.mark.parametrize("elo_rating, expected_status", [
    (0.9, 422),  # Below minimum
    (7.1, 422),  # Above maximum
    (1.0, 201),  # Minimum allowed - Corrected to 201 Created
    (7.0, 201),  # Maximum allowed - Corrected to 201 Created
    (4.5, 201),  # Valid value - Corrected to 201 Created
])
def test_create_user_with_elo_rating_validation(
    client: TestClient, db_session: Session, elo_rating: float, expected_status: int
):
    """
    Test creating a user with various elo_rating values to check validation.
    """
    user_data = {
        "full_name": "Test User",
        "email": f"testuser_{elo_rating}@example.com",
        "password": "a_secure_password",
        "elo_rating": elo_rating,
    }

    response = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json=user_data,
    )

    assert response.status_code == expected_status

    if expected_status == 201:
        # Verify the user was actually created with the correct rating
        user = get_user_by_email(db_session, email=user_data["email"])
        assert user is not None
        assert user.elo_rating == elo_rating
    else:
        # Verify the user was not created
        user = get_user_by_email(db_session, email=user_data["email"])
        assert user is None

@pytest.mark.parametrize("position, expected_status", [
    ("LEFT", 201),
    ("RIGHT", 201),
    (None, 201),
    ("INVALID_POSITION", 422),
])
def test_create_user_with_preferred_position(
    client: TestClient, db_session: Session, position: str, expected_status: int
):
    """
    Test creating a user with various preferred_position values.
    """
    user_data = {
        "full_name": "Position User",
        "email": f"position_user_{position}@example.com",
        "password": "a_secure_password",
        "preferred_position": position,
    }

    response = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json=user_data,
    )

    assert response.status_code == expected_status

    if expected_status == 201:
        user = get_user_by_email(db_session, email=user_data["email"])
        assert user is not None
        assert user.preferred_position == position
    else:
        user = get_user_by_email(db_session, email=user_data["email"])
        assert user is None

def test_update_user_me(client: TestClient, db_session: Session, test_user: models.User, user_auth_headers: dict):
    # Test updating preferred_position and full_name
    update_data = {"preferred_position": "RIGHT", "full_name": "New Name"}
    response = client.put(f"{settings.API_V1_STR}/users/me", json=update_data, headers=user_auth_headers)
    assert response.status_code == 200
    updated_user = response.json()
    assert updated_user["preferred_position"] == "RIGHT"
    assert updated_user["full_name"] == "New Name"

    # Test that elo_rating cannot be updated
    update_data = {"elo_rating": 7.0}
    response = client.put(f"{settings.API_V1_STR}/users/me", json=update_data, headers=user_auth_headers)
    assert response.status_code == 200
    updated_user = response.json()
    assert updated_user["elo_rating"] != 7.0 