import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud, models, schemas

def test_get_leaderboard(client: TestClient, db_session: Session):
    # Create some users with different ELO ratings
    user1 = crud.user_crud.create_user(db_session, schemas.UserCreate(email="user1@test.com", password="password1", full_name="User One", elo_rating=1.5))
    user2 = crud.user_crud.create_user(db_session, schemas.UserCreate(email="user2@test.com", password="password2", full_name="User Two", elo_rating=2.5))
    user3 = crud.user_crud.create_user(db_session, schemas.UserCreate(email="user3@test.com", password="password3", full_name="User Three", elo_rating=3.5))

    response = client.get("/api/v1/leaderboard")
    assert response.status_code == 200
    leaderboard = response.json()

    assert leaderboard["total"] == 3
    assert leaderboard["limit"] == 10
    assert leaderboard["offset"] == 0
    assert len(leaderboard["users"]) == 3

    # Verify the order
    assert leaderboard["users"][0]["id"] == user3.id
    assert leaderboard["users"][1]["id"] == user2.id
    assert leaderboard["users"][2]["id"] == user1.id 