import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from app.routers.games import validate_game_exists, validate_game_not_scored, validate_winning_team
from app import models, schemas, crud

def test_validate_game_exists_found():
    mock_db = Mock(spec=Session)
    mock_game = models.Game(id=1)
    
    with patch('app.routers.games.crud.game.get_with_teams', return_value=mock_game) as mock_get_game:
        game = validate_game_exists(mock_db, 1)
        mock_get_game.assert_called_once_with(mock_db, game_id=1)
        assert game == mock_game

def test_validate_game_exists_not_found():
    mock_db = Mock(spec=Session)
    
    with patch('app.routers.games.crud.game.get_with_teams', return_value=None) as mock_get_game:
        with pytest.raises(HTTPException) as exc_info:
            validate_game_exists(mock_db, 1)
        
        assert exc_info.value.status_code == 404
        assert "Game not found" in exc_info.value.detail
        mock_get_game.assert_called_once_with(mock_db, game_id=1)

def test_validate_game_not_scored():
    mock_game = models.Game(id=1, winning_team_id=None)
    validate_game_not_scored(mock_game) # Should not raise

def test_validate_game_already_scored():
    mock_game = models.Game(id=1, winning_team_id=1)
    with pytest.raises(HTTPException) as exc_info:
        validate_game_not_scored(mock_game)
    
    assert exc_info.value.status_code == 400
    assert "Game result has already been submitted" in exc_info.value.detail

def test_validate_winning_team_found():
    mock_db = Mock(spec=Session)
    mock_team = models.Team(id=1, name="Test Team")
    mock_db.query.return_value.filter.return_value.first.return_value = mock_team
    
    team = validate_winning_team(mock_db, 1)
    assert team == mock_team

def test_validate_winning_team_not_found():
    mock_db = Mock(spec=Session)
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    with pytest.raises(HTTPException) as exc_info:
        validate_winning_team(mock_db, 1)
        
    assert exc_info.value.status_code == 404
    assert "Winning team not found" in exc_info.value.detail

def test_submit_game_result_elo_integration(
    client: TestClient,
    db_session: Session,
    test_user: models.User,
    user_auth_headers: dict
):
    # Create players and teams
    player1 = crud.user.create(db_session, obj_in=schemas.UserCreate(email="p1@test.com", password="p1", full_name="p1"))
    player2 = crud.user.create(db_session, obj_in=schemas.UserCreate(email="p2@test.com", password="p2", full_name="p2"))
    player3 = crud.user.create(db_session, obj_in=schemas.UserCreate(email="p3@test.com", password="p3", full_name="p3"))
    player4 = crud.user.create(db_session, obj_in=schemas.UserCreate(email="p4@test.com", password="p4", full_name="p4"))

    team1 = crud.team.create_with_players(db_session, name="Team A", players=[player1, player2])
    team2 = crud.team.create_with_players(db_session, name="Team B", players=[player3, player4])

    # Create a booking
    booking = crud.booking.create_with_owner(
        db_session, 
        obj_in=schemas.BookingCreate(
            club_id=1, 
            court_id=1, 
            start_time=datetime.utcnow(), 
            end_time=datetime.utcnow() + timedelta(hours=1)
        ),
        user_id=test_user.id
    )

    # Create a game
    game = crud.game.create_with_booking(
        db_session,
        booking_id=booking.id,
        game_type="PUBLIC",
        skill_level="Intermediate",
    )
    game.team1_id = team1.id
    game.team2_id = team2.id
    db_session.add(game)
    db_session.commit()
    db_session.refresh(game)


    # Call the endpoint
    response = client.post(
        f"/api/v1/games/{game.id}/result",
        json={"winning_team_id": team1.id},
        headers=user_auth_headers
    )

    assert response.status_code == 200
    
    # Check that ELO ratings have been updated
    db_session.refresh(player1)
    db_session.refresh(player3)
    
    assert player1.elo_rating > 1500
    assert player3.elo_rating < 1500 