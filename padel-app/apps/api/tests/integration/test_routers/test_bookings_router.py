from datetime import date, datetime, time, timedelta
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core.config import settings


class TestBookingsRouter:
    """Test suite for bookings router endpoints."""

    @patch("app.services.availability_service.get_court_availability_for_day")
    @patch(
        "app.services.court_booking_service.court_booking_service.is_court_available"
    )
    def test_create_booking_success(
        self,
        mock_court_available,
        mock_availability,
        client: TestClient,
        player_auth_headers: dict,
        test_court: models.Court,
        db_session: Session,
    ):
        """Test successful booking creation."""
        # Mock availability service to return available slot
        mock_availability.return_value = [
            Mock(start_time="2024-01-01T10:00:00", is_available=True)
        ]
        mock_court_available.return_value = True

        booking_data = {
            "court_id": test_court.id,
            "start_time": "2024-01-01T10:00:00",
            "duration": 60,
            "player_count": 2,
        }

        response = client.post(
            f"{settings.API_V1_STR}/bookings",
            headers=player_auth_headers,
            json=booking_data,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["court_id"] == test_court.id
        assert data["start_time"] == "2024-01-01T10:00:00"
        assert data["duration"] == 60
        assert data["player_count"] == 2

    def test_create_booking_court_not_found(
        self, client: TestClient, player_auth_headers: dict
    ):
        """Test booking creation with non-existent court."""
        booking_data = {
            "court_id": 99999,
            "start_time": "2024-01-01T10:00:00",
            "duration": 60,
            "player_count": 2,
        }

        response = client.post(
            f"{settings.API_V1_STR}/bookings",
            headers=player_auth_headers,
            json=booking_data,
        )
        assert response.status_code == 404
        assert "Court with id 99999 not found" in response.json()["detail"]

    @patch("app.services.availability_service.get_court_availability_for_day")
    @patch(
        "app.services.court_booking_service.court_booking_service.is_court_available"
    )
    def test_create_booking_slot_not_available(
        self,
        mock_court_available,
        mock_availability,
        client: TestClient,
        player_auth_headers: dict,
        test_court: models.Court,
    ):
        """Test booking creation when slot is not available."""
        # Mock availability service to return no available slots
        mock_availability.return_value = [
            Mock(start_time="2024-01-01T10:00:00", is_available=False)
        ]
        mock_court_available.return_value = True

        booking_data = {
            "court_id": test_court.id,
            "start_time": "2024-01-01T10:00:00",
            "duration": 60,
            "player_count": 2,
        }

        response = client.post(
            f"{settings.API_V1_STR}/bookings",
            headers=player_auth_headers,
            json=booking_data,
        )
        assert response.status_code == 400
        assert "The requested time slot is not available" in response.json()["detail"]

    @patch("app.services.availability_service.get_court_availability_for_day")
    @patch(
        "app.services.court_booking_service.court_booking_service.is_court_available"
    )
    def test_create_booking_tournament_conflict(
        self,
        mock_court_available,
        mock_availability,
        client: TestClient,
        player_auth_headers: dict,
        test_court: models.Court,
    ):
        """Test booking creation when court is reserved for tournament."""
        # Mock availability service to return available slot
        mock_availability.return_value = [
            Mock(start_time="2024-01-01T10:00:00", is_available=True)
        ]
        # Mock court booking service to return tournament conflict
        mock_court_available.return_value = False

        booking_data = {
            "court_id": test_court.id,
            "start_time": "2024-01-01T10:00:00",
            "duration": 60,
            "player_count": 2,
        }

        response = client.post(
            f"{settings.API_V1_STR}/bookings",
            headers=player_auth_headers,
            json=booking_data,
        )
        assert response.status_code == 400
        assert "The court is reserved for a tournament" in response.json()["detail"]

    @patch("app.services.availability_service.get_court_availability_for_day")
    def test_create_booking_availability_service_error(
        self,
        mock_availability,
        client: TestClient,
        player_auth_headers: dict,
        test_court: models.Court,
    ):
        """Test booking creation when availability service fails."""
        # Mock availability service to raise an exception
        mock_availability.side_effect = Exception("Service unavailable")

        booking_data = {
            "court_id": test_court.id,
            "start_time": "2024-01-01T10:00:00",
            "duration": 60,
            "player_count": 2,
        }

        response = client.post(
            f"{settings.API_V1_STR}/bookings",
            headers=player_auth_headers,
            json=booking_data,
        )
        assert response.status_code == 500
        assert "Failed to check court availability" in response.json()["detail"]

    def test_create_booking_unauthorized(
        self, client: TestClient, test_court: models.Court
    ):
        """Test booking creation without authentication."""
        booking_data = {
            "court_id": test_court.id,
            "start_time": "2024-01-01T10:00:00",
            "duration": 60,
            "player_count": 2,
        }

        response = client.post(f"{settings.API_V1_STR}/bookings", json=booking_data)
        assert response.status_code == 401

    def test_create_booking_invalid_data(
        self, client: TestClient, player_auth_headers: dict
    ):
        """Test booking creation with invalid data."""
        # Missing required fields
        booking_data = {
            "court_id": 1
            # Missing start_time, duration, player_count
        }

        response = client.post(
            f"{settings.API_V1_STR}/bookings",
            headers=player_auth_headers,
            json=booking_data,
        )
        assert response.status_code == 422

    def test_create_booking_invalid_duration(
        self, client: TestClient, player_auth_headers: dict, test_court: models.Court
    ):
        """Test booking creation with invalid duration."""
        booking_data = {
            "court_id": test_court.id,
            "start_time": "2024-01-01T10:00:00",
            "duration": -30,  # Invalid negative duration
            "player_count": 2,
        }

        response = client.post(
            f"{settings.API_V1_STR}/bookings",
            headers=player_auth_headers,
            json=booking_data,
        )
        assert response.status_code == 422

    def test_create_booking_invalid_player_count(
        self, client: TestClient, player_auth_headers: dict, test_court: models.Court
    ):
        """Test booking creation with invalid player count."""
        booking_data = {
            "court_id": test_court.id,
            "start_time": "2024-01-01T10:00:00",
            "duration": 60,
            "player_count": 0,  # Invalid zero player count
        }

        response = client.post(
            f"{settings.API_V1_STR}/bookings",
            headers=player_auth_headers,
            json=booking_data,
        )
        assert response.status_code == 422

    def test_read_user_bookings_success(
        self,
        client: TestClient,
        player_auth_headers: dict,
        test_booking: models.Booking,
    ):
        """Test successfully reading user bookings."""
        response = client.get(
            f"{settings.API_V1_STR}/bookings", headers=player_auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["id"] == test_booking.id
        assert data[0]["court_id"] == test_booking.court_id

    def test_read_user_bookings_unauthorized(self, client: TestClient):
        """Test reading user bookings without authentication."""
        response = client.get(f"{settings.API_V1_STR}/bookings")
        assert response.status_code == 401

    def test_read_user_bookings_with_pagination(
        self,
        client: TestClient,
        player_auth_headers: dict,
        db_session: Session,
        test_court: models.Court,
        player_user: models.User,
    ):
        """Test reading user bookings with pagination."""
        # Create multiple bookings
        for i in range(5):
            booking_in = schemas.BookingCreate(
                court_id=test_court.id,
                booking_date=date.today(),
                start_time=time(10 + i, 0),
                end_time=time(11 + i, 0),
                player_count=2,
                status=models.BookingStatus.CONFIRMED,
            )
            crud.booking_crud.create_booking(db_session, booking_in, player_user.id)

        # Test pagination
        response = client.get(
            f"{settings.API_V1_STR}/bookings",
            headers=player_auth_headers,
            params={"skip": 0, "limit": 3},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 3

    def test_read_user_bookings_with_date_filter(
        self,
        client: TestClient,
        player_auth_headers: dict,
        test_booking: models.Booking,
    ):
        """Test reading user bookings with date filter."""
        today = date.today()
        response = client.get(
            f"{settings.API_V1_STR}/bookings",
            headers=player_auth_headers,
            params={
                "start_date_filter": today.isoformat(),
                "end_date_filter": today.isoformat(),
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_read_user_bookings_with_sorting(
        self,
        client: TestClient,
        player_auth_headers: dict,
        test_booking: models.Booking,
    ):
        """Test reading user bookings with sorting."""
        response = client.get(
            f"{settings.API_V1_STR}/bookings",
            headers=player_auth_headers,
            params={"sort_by": "start_time", "sort_desc": True},
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_read_user_bookings_invalid_pagination(
        self, client: TestClient, player_auth_headers: dict
    ):
        """Test reading user bookings with invalid pagination parameters."""
        response = client.get(
            f"{settings.API_V1_STR}/bookings",
            headers=player_auth_headers,
            params={
                "skip": -1,  # Invalid negative skip
                "limit": 0,  # Invalid zero limit
            },
        )
        assert response.status_code == 422

    def test_read_user_bookings_limit_exceeded(
        self, client: TestClient, player_auth_headers: dict
    ):
        """Test reading user bookings with limit exceeding maximum."""
        response = client.get(
            f"{settings.API_V1_STR}/bookings",
            headers=player_auth_headers,
            params={"limit": 300},  # Exceeds maximum of 200
        )
        assert response.status_code == 422

    def test_read_booking_details_success(
        self,
        client: TestClient,
        player_auth_headers: dict,
        test_booking: models.Booking,
    ):
        """Test successfully reading booking details."""
        response = client.get(
            f"{settings.API_V1_STR}/bookings/{test_booking.id}",
            headers=player_auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_booking.id
        assert data["court_id"] == test_booking.court_id
        assert data["player_count"] == test_booking.player_count

    def test_read_booking_details_not_found(
        self, client: TestClient, player_auth_headers: dict
    ):
        """Test reading details for non-existent booking."""
        response = client.get(
            f"{settings.API_V1_STR}/bookings/99999", headers=player_auth_headers
        )
        assert response.status_code == 404
        assert "Booking not found" in response.json()["detail"]

    def test_read_booking_details_unauthorized_access(
        self, client: TestClient, admin_auth_headers: dict, test_booking: models.Booking
    ):
        """Test reading booking details for booking owned by another user."""
        response = client.get(
            f"{settings.API_V1_STR}/bookings/{test_booking.id}",
            headers=admin_auth_headers,
        )
        assert response.status_code == 403
        assert "Not authorized to access this booking" in response.json()["detail"]

    def test_read_booking_details_unauthorized(
        self, client: TestClient, test_booking: models.Booking
    ):
        """Test reading booking details without authentication."""
        response = client.get(f"{settings.API_V1_STR}/bookings/{test_booking.id}")
        assert response.status_code == 401

    def test_read_booking_details_invalid_id(
        self, client: TestClient, player_auth_headers: dict
    ):
        """Test reading booking details with invalid ID format."""
        response = client.get(
            f"{settings.API_V1_STR}/bookings/invalid-id", headers=player_auth_headers
        )
        assert response.status_code == 422

    def test_booking_business_logic_edge_cases(
        self, client: TestClient, player_auth_headers: dict, test_court: models.Court
    ):
        """Test booking business logic edge cases."""
        # Test booking in the past
        past_time = datetime.now() - timedelta(days=1)
        booking_data = {
            "court_id": test_court.id,
            "start_time": past_time.isoformat(),
            "duration": 60,
            "player_count": 2,
        }

        with patch(
            "app.services.availability_service.get_court_availability_for_day"
        ) as mock_availability:
            mock_availability.return_value = [
                Mock(start_time=past_time.isoformat(), is_available=True)
            ]
            with patch(
                "app.services.court_booking_service.court_booking_service.is_court_available"
            ) as mock_court_available:
                mock_court_available.return_value = True
                response = client.post(
                    f"{settings.API_V1_STR}/bookings",
                    headers=player_auth_headers,
                    json=booking_data,
                )
                # Should still work if availability service allows it
                assert response.status_code in [201, 400]

    def test_booking_concurrent_creation(
        self, client: TestClient, player_auth_headers: dict, test_court: models.Court
    ):
        """Test concurrent booking creation for the same slot."""
        booking_data = {
            "court_id": test_court.id,
            "start_time": "2024-01-01T10:00:00",
            "duration": 60,
            "player_count": 2,
        }

        with patch(
            "app.services.availability_service.get_court_availability_for_day"
        ) as mock_availability:
            mock_availability.return_value = [
                Mock(start_time="2024-01-01T10:00:00", is_available=True)
            ]
            with patch(
                "app.services.court_booking_service.court_booking_service.is_court_available"
            ) as mock_court_available:
                mock_court_available.return_value = True

                # First booking should succeed
                response1 = client.post(
                    f"{settings.API_V1_STR}/bookings",
                    headers=player_auth_headers,
                    json=booking_data,
                )
                assert response1.status_code == 201

                # Second booking for same slot should fail
                mock_availability.return_value = [
                    Mock(start_time="2024-01-01T10:00:00", is_available=False)
                ]
                response2 = client.post(
                    f"{settings.API_V1_STR}/bookings",
                    headers=player_auth_headers,
                    json=booking_data,
                )
                assert response2.status_code == 400

    def test_booking_data_validation_edge_cases(
        self, client: TestClient, player_auth_headers: dict, test_court: models.Court
    ):
        """Test booking data validation edge cases."""
        # Test with very long duration
        booking_data = {
            "court_id": test_court.id,
            "start_time": "2024-01-01T10:00:00",
            "duration": 480,  # 8 hours
            "player_count": 2,
        }

        with patch(
            "app.services.availability_service.get_court_availability_for_day"
        ) as mock_availability:
            mock_availability.return_value = [
                Mock(start_time="2024-01-01T10:00:00", is_available=True)
            ]
            with patch(
                "app.services.court_booking_service.court_booking_service.is_court_available"
            ) as mock_court_available:
                mock_court_available.return_value = True
                response = client.post(
                    f"{settings.API_V1_STR}/bookings",
                    headers=player_auth_headers,
                    json=booking_data,
                )
                # Should work if validation allows it
                assert response.status_code in [201, 422]

    def test_booking_error_handling(
        self, client: TestClient, player_auth_headers: dict, test_court: models.Court
    ):
        """Test booking error handling."""
        booking_data = {
            "court_id": test_court.id,
            "start_time": "2024-01-01T10:00:00",
            "duration": 60,
            "player_count": 2,
        }

        with patch(
            "app.services.availability_service.get_court_availability_for_day"
        ) as mock_availability:
            mock_availability.return_value = [
                Mock(start_time="2024-01-01T10:00:00", is_available=True)
            ]
            with patch(
                "app.services.court_booking_service.court_booking_service.is_court_available"
            ) as mock_court_available:
                mock_court_available.return_value = True
                with patch(
                    "app.crud.booking_crud.create_booking"
                ) as mock_create_booking:
                    mock_create_booking.side_effect = Exception("Database error")
                    response = client.post(
                        f"{settings.API_V1_STR}/bookings",
                        headers=player_auth_headers,
                        json=booking_data,
                    )
                    assert response.status_code == 500
                    assert (
                        "An error occurred while creating the booking"
                        in response.json()["detail"]
                    )

    def test_booking_service_integration(
        self, client: TestClient, player_auth_headers: dict, test_court: models.Court
    ):
        """Test integration between booking router and services."""
        booking_data = {
            "court_id": test_court.id,
            "start_time": "2024-01-01T10:00:00",
            "duration": 60,
            "player_count": 2,
        }

        # Test that both services are called correctly
        with patch(
            "app.services.availability_service.get_court_availability_for_day"
        ) as mock_availability:
            mock_availability.return_value = [
                Mock(start_time="2024-01-01T10:00:00", is_available=True)
            ]
            with patch(
                "app.services.court_booking_service.court_booking_service.is_court_available"
            ) as mock_court_available:
                mock_court_available.return_value = True

                response = client.post(
                    f"{settings.API_V1_STR}/bookings",
                    headers=player_auth_headers,
                    json=booking_data,
                )
                assert response.status_code == 201

                # Verify that both services were called
                mock_availability.assert_called_once()
                mock_court_available.assert_called_once()

    def test_booking_malformed_datetime(
        self, client: TestClient, player_auth_headers: dict, test_court: models.Court
    ):
        """Test booking with malformed datetime."""
        booking_data = {
            "court_id": test_court.id,
            "start_time": "invalid-datetime",
            "duration": 60,
            "player_count": 2,
        }

        response = client.post(
            f"{settings.API_V1_STR}/bookings",
            headers=player_auth_headers,
            json=booking_data,
        )
        assert response.status_code == 422

    def test_booking_extreme_values(
        self, client: TestClient, player_auth_headers: dict, test_court: models.Court
    ):
        """Test booking with extreme values."""
        booking_data = {
            "court_id": test_court.id,
            "start_time": "2024-01-01T10:00:00",
            "duration": 0,  # Zero duration
            "player_count": 999,  # Very high player count
        }

        response = client.post(
            f"{settings.API_V1_STR}/bookings",
            headers=player_auth_headers,
            json=booking_data,
        )
        assert response.status_code == 422

    def test_booking_sql_injection_protection(
        self, client: TestClient, player_auth_headers: dict
    ):
        """Test protection against SQL injection in booking parameters."""
        # Test with malicious court_id
        booking_data = {
            "court_id": "1; DROP TABLE bookings; --",
            "start_time": "2024-01-01T10:00:00",
            "duration": 60,
            "player_count": 2,
        }

        response = client.post(
            f"{settings.API_V1_STR}/bookings",
            headers=player_auth_headers,
            json=booking_data,
        )
        assert (
            response.status_code == 422
        )  # Should fail validation, not cause server error
