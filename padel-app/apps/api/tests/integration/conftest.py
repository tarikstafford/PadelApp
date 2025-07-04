from datetime import date, time
from io import BytesIO
from typing import Any

import pytest
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core.security import create_access_token


@pytest.fixture
def admin_user(db_session: Session) -> models.User:
    """Create a test admin user."""
    user_in = schemas.UserCreate(
        email="admin@example.com",
        password="adminpass123",
        full_name="Admin User",
        phone_number="1234567890",
        role=models.UserRole.ADMIN,
    )
    return crud.user_crud.create_user(db_session, user_in)


@pytest.fixture
def club_admin_user(db_session: Session) -> models.User:
    """Create a test club admin user."""
    user_in = schemas.UserCreate(
        email="clubadmin@example.com",
        password="clubadminpass123",
        full_name="Club Admin User",
        phone_number="1234567891",
        role=models.UserRole.CLUB_ADMIN,
    )
    return crud.user_crud.create_user(db_session, user_in)


@pytest.fixture
def super_admin_user(db_session: Session) -> models.User:
    """Create a test super admin user."""
    user_in = schemas.UserCreate(
        email="superadmin@example.com",
        password="superadminpass123",
        full_name="Super Admin User",
        phone_number="1234567892",
        role=models.UserRole.SUPER_ADMIN,
    )
    return crud.user_crud.create_user(db_session, user_in)


@pytest.fixture
def player_user(db_session: Session) -> models.User:
    """Create a test player user."""
    user_in = schemas.UserCreate(
        email="player@example.com",
        password="playerpass123",
        full_name="Player User",
        phone_number="1234567893",
        role=models.UserRole.PLAYER,
    )
    return crud.user_crud.create_user(db_session, user_in)


@pytest.fixture
def test_club(db_session: Session, club_admin_user: models.User) -> models.Club:
    """Create a test club."""
    club_in = schemas.ClubCreate(
        name="Test Club",
        description="A test club for testing",
        address="123 Test St",
        city="Test City",
        postal_code="12345",
        phone="555-0123",
        email="test@club.com",
        opening_time="08:00",
        closing_time="22:00",
        amenities="WiFi, Parking, Showers",
        owner_id=club_admin_user.id,
    )
    return crud.club_crud.create_club(db_session, club_in)


@pytest.fixture
def test_court(db_session: Session, test_club: models.Club) -> models.Court:
    """Create a test court."""
    court_in = schemas.CourtCreate(
        name="Court 1", description="Test court description", club_id=test_club.id
    )
    return crud.court_crud.create_court(db_session, court_in, test_club.id)


@pytest.fixture
def test_booking(
    db_session: Session, test_court: models.Court, player_user: models.User
) -> models.Booking:
    """Create a test booking."""
    booking_in = schemas.BookingCreate(
        court_id=test_court.id,
        booking_date=date.today(),
        start_time=time(10, 0),
        end_time=time(11, 0),
        player_count=2,
        status=models.BookingStatus.CONFIRMED,
    )
    return crud.booking_crud.create_booking(db_session, booking_in, player_user.id)


@pytest.fixture
def test_game(db_session: Session, test_booking: models.Booking) -> models.Game:
    """Create a test game."""
    game_in = schemas.GameCreate(
        booking_id=test_booking.id,
        game_date=date.today(),
        start_time=time(10, 0),
        end_time=time(11, 0),
        max_players=4,
        skill_level="intermediate",
        description="Test game",
    )
    return crud.game_crud.create_game(db_session, game_in, test_booking.user_id)


@pytest.fixture
def admin_auth_headers(admin_user: models.User) -> dict[str, str]:
    """Get authentication headers for admin user."""
    token = create_access_token(subject=admin_user.email, role=admin_user.role.value)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def club_admin_auth_headers(club_admin_user: models.User) -> dict[str, str]:
    """Get authentication headers for club admin user."""
    token = create_access_token(
        subject=club_admin_user.email, role=club_admin_user.role.value
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def super_admin_auth_headers(super_admin_user: models.User) -> dict[str, str]:
    """Get authentication headers for super admin user."""
    token = create_access_token(
        subject=super_admin_user.email, role=super_admin_user.role.value
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def player_auth_headers(player_user: models.User) -> dict[str, str]:
    """Get authentication headers for player user."""
    token = create_access_token(subject=player_user.email, role=player_user.role.value)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def mock_image_file():
    """Create a mock image file for testing file uploads."""
    content = b"fake image content"
    return BytesIO(content)


@pytest.fixture
def sample_club_data() -> dict[str, Any]:
    """Sample club data for testing."""
    return {
        "name": "Sample Club",
        "description": "A sample club for testing",
        "address": "456 Sample Ave",
        "city": "Sample City",
        "postal_code": "67890",
        "phone": "555-0456",
        "email": "sample@club.com",
        "opening_time": "07:00",
        "closing_time": "23:00",
        "amenities": "Pool, Gym, Sauna",
    }


@pytest.fixture
def sample_court_data() -> dict[str, Any]:
    """Sample court data for testing."""
    return {
        "name": "Sample Court",
        "description": "A sample court for testing",
        "surface_type": "synthetic",
        "is_covered": True,
    }


@pytest.fixture
def sample_booking_data() -> dict[str, Any]:
    """Sample booking data for testing."""
    return {
        "booking_date": date.today().isoformat(),
        "start_time": "10:00",
        "end_time": "11:00",
        "player_count": 2,
    }


@pytest.fixture
def sample_game_data() -> dict[str, Any]:
    """Sample game data for testing."""
    return {
        "game_date": date.today().isoformat(),
        "start_time": "10:00",
        "end_time": "11:00",
        "max_players": 4,
        "skill_level": "intermediate",
        "description": "Sample game for testing",
    }


@pytest.fixture
def sample_user_data() -> dict[str, Any]:
    """Sample user data for testing."""
    return {
        "email": "newuser@example.com",
        "password": "newuserpass123",
        "full_name": "New User",
        "phone_number": "1234567894",
        "elo_rating": 3.5,
        "preferred_position": "LEFT",
    }


@pytest.fixture
def invalid_auth_headers() -> dict[str, str]:
    """Get invalid authentication headers for testing unauthorized access."""
    return {"Authorization": "Bearer invalid_token"}


@pytest.fixture
def expired_auth_headers() -> dict[str, str]:
    """Get expired authentication headers for testing."""
    # Create a token that's already expired
    token = create_access_token(
        subject="expired@example.com", role="PLAYER", expires_delta=-1
    )
    return {"Authorization": f"Bearer {token}"}
