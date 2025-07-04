from datetime import date
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import models
from app.core.config import settings


class TestAdminRouter:
    """Test suite for admin router endpoints."""

    def test_admin_route_access_with_valid_admin(
        self, client: TestClient, admin_auth_headers: dict
    ):
        """Test that admin route is accessible with valid admin credentials."""
        response = client.get(
            f"{settings.API_V1_STR}/admin/test", headers=admin_auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "admin@example.com"
        assert data["role"] == "ADMIN"

    def test_admin_route_access_with_club_admin(
        self, client: TestClient, club_admin_auth_headers: dict
    ):
        """Test that admin route is accessible with club admin credentials."""
        response = client.get(
            f"{settings.API_V1_STR}/admin/test", headers=club_admin_auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "clubadmin@example.com"
        assert data["role"] == "CLUB_ADMIN"

    def test_admin_route_access_with_super_admin(
        self, client: TestClient, super_admin_auth_headers: dict
    ):
        """Test that admin route is accessible with super admin credentials."""
        response = client.get(
            f"{settings.API_V1_STR}/admin/test", headers=super_admin_auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "superadmin@example.com"
        assert data["role"] == "SUPER_ADMIN"

    def test_admin_route_access_denied_for_player(
        self, client: TestClient, player_auth_headers: dict
    ):
        """Test that admin route is not accessible for regular players."""
        response = client.get(
            f"{settings.API_V1_STR}/admin/test", headers=player_auth_headers
        )
        assert response.status_code == 403
        assert "is not permitted to access this resource" in response.json()["detail"]

    def test_admin_route_access_denied_unauthenticated(self, client: TestClient):
        """Test that admin route is not accessible without authentication."""
        response = client.get(f"{settings.API_V1_STR}/admin/test")
        assert response.status_code == 401

    def test_admin_route_access_denied_invalid_token(
        self, client: TestClient, invalid_auth_headers: dict
    ):
        """Test that admin route is not accessible with invalid token."""
        response = client.get(
            f"{settings.API_V1_STR}/admin/test", headers=invalid_auth_headers
        )
        assert response.status_code == 401

    def test_read_owned_club_success(
        self, client: TestClient, club_admin_auth_headers: dict, test_club: models.Club
    ):
        """Test successfully reading owned club."""
        response = client.get(
            f"{settings.API_V1_STR}/admin/my-club", headers=club_admin_auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_club.id
        assert data["name"] == test_club.name

    def test_read_owned_club_not_found(
        self, client: TestClient, admin_auth_headers: dict
    ):
        """Test reading owned club when user doesn't own a club."""
        response = client.get(
            f"{settings.API_V1_STR}/admin/my-club", headers=admin_auth_headers
        )
        assert response.status_code == 404
        assert "does not own a club" in response.json()["detail"]

    def test_update_club_success(
        self, client: TestClient, club_admin_auth_headers: dict, test_club: models.Club
    ):
        """Test successfully updating a club."""
        update_data = {
            "name": "Updated Club Name",
            "description": "Updated description",
        }
        response = client.put(
            f"{settings.API_V1_STR}/admin/club/{test_club.id}",
            headers=club_admin_auth_headers,
            json=update_data,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Club Name"
        assert data["description"] == "Updated description"

    def test_update_club_not_found(
        self, client: TestClient, club_admin_auth_headers: dict
    ):
        """Test updating non-existent club."""
        update_data = {"name": "Updated Club Name"}
        response = client.put(
            f"{settings.API_V1_STR}/admin/club/99999",
            headers=club_admin_auth_headers,
            json=update_data,
        )
        assert response.status_code == 404
        assert "Club not found" in response.json()["detail"]

    def test_read_club_success(
        self, client: TestClient, club_admin_auth_headers: dict, test_club: models.Club
    ):
        """Test successfully reading a club."""
        response = client.get(
            f"{settings.API_V1_STR}/admin/club/{test_club.id}",
            headers=club_admin_auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_club.id
        assert data["name"] == test_club.name

    def test_read_club_not_found(
        self, client: TestClient, club_admin_auth_headers: dict
    ):
        """Test reading non-existent club."""
        response = client.get(
            f"{settings.API_V1_STR}/admin/club/99999", headers=club_admin_auth_headers
        )
        assert response.status_code == 404
        assert "Club not found" in response.json()["detail"]

    def test_read_club_courts_success(
        self,
        client: TestClient,
        club_admin_auth_headers: dict,
        test_club: models.Club,
        test_court: models.Court,
    ):
        """Test successfully reading club courts."""
        response = client.get(
            f"{settings.API_V1_STR}/admin/club/{test_club.id}/courts",
            headers=club_admin_auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == test_court.id
        assert data[0]["name"] == test_court.name

    def test_read_club_schedule_success(
        self,
        client: TestClient,
        club_admin_auth_headers: dict,
        test_club: models.Club,
        test_court: models.Court,
        test_booking: models.Booking,
    ):
        """Test successfully reading club schedule."""
        response = client.get(
            f"{settings.API_V1_STR}/admin/club/{test_club.id}/schedule",
            headers=club_admin_auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "courts" in data
        assert "bookings" in data
        assert len(data["courts"]) == 1
        assert len(data["bookings"]) >= 1

    def test_read_club_schedule_with_date_range(
        self, client: TestClient, club_admin_auth_headers: dict, test_club: models.Club
    ):
        """Test reading club schedule with date range."""
        start_date = date.today()
        end_date = date.today()
        response = client.get(
            f"{settings.API_V1_STR}/admin/club/{test_club.id}/schedule",
            headers=club_admin_auth_headers,
            params={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "courts" in data
        assert "bookings" in data

    def test_read_club_schedule_invalid_date_range(
        self, client: TestClient, club_admin_auth_headers: dict, test_club: models.Club
    ):
        """Test reading club schedule with invalid date range."""
        start_date = date.today()
        end_date = date(2020, 1, 1)  # End date before start date
        response = client.get(
            f"{settings.API_V1_STR}/admin/club/{test_club.id}/schedule",
            headers=club_admin_auth_headers,
            params={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
        )
        assert response.status_code == 400
        assert "End date cannot be earlier than start date" in response.json()["detail"]

    def test_get_my_club_schedule_success(
        self, client: TestClient, club_admin_auth_headers: dict, test_club: models.Club
    ):
        """Test getting my club schedule."""
        response = client.get(
            f"{settings.API_V1_STR}/admin/my-club/schedule",
            headers=club_admin_auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "courts" in data
        assert "bookings" in data

    def test_get_my_club_schedule_no_club(
        self, client: TestClient, admin_auth_headers: dict
    ):
        """Test getting my club schedule when admin doesn't own a club."""
        response = client.get(
            f"{settings.API_V1_STR}/admin/my-club/schedule", headers=admin_auth_headers
        )
        assert response.status_code == 404
        assert "does not own a club" in response.json()["detail"]

    def test_get_my_club_schedule_invalid_date_format(
        self, client: TestClient, club_admin_auth_headers: dict, test_club: models.Club
    ):
        """Test getting my club schedule with invalid date format."""
        response = client.get(
            f"{settings.API_V1_STR}/admin/my-club/schedule",
            headers=club_admin_auth_headers,
            params={"start_date": "invalid-date"},
        )
        assert response.status_code == 400
        assert "Invalid date format" in response.json()["detail"]

    def test_read_owned_club_courts_success(
        self,
        client: TestClient,
        club_admin_auth_headers: dict,
        test_club: models.Club,
        test_court: models.Court,
    ):
        """Test successfully reading owned club courts."""
        response = client.get(
            f"{settings.API_V1_STR}/admin/my-club/courts",
            headers=club_admin_auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == test_court.id
        assert data[0]["name"] == test_court.name

    def test_read_owned_club_courts_no_club(
        self, client: TestClient, admin_auth_headers: dict
    ):
        """Test reading owned club courts when admin doesn't own a club."""
        response = client.get(
            f"{settings.API_V1_STR}/admin/my-club/courts", headers=admin_auth_headers
        )
        assert response.status_code == 404
        assert "does not own a club" in response.json()["detail"]

    def test_create_owned_club_court_success(
        self,
        client: TestClient,
        club_admin_auth_headers: dict,
        test_club: models.Club,
        sample_court_data: dict,
    ):
        """Test successfully creating a court for owned club."""
        response = client.post(
            f"{settings.API_V1_STR}/admin/my-club/courts",
            headers=club_admin_auth_headers,
            json=sample_court_data,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_court_data["name"]
        assert data["description"] == sample_court_data["description"]
        assert data["club_id"] == test_club.id

    def test_create_owned_club_court_no_club(
        self, client: TestClient, admin_auth_headers: dict, sample_court_data: dict
    ):
        """Test creating a court when admin doesn't own a club."""
        response = client.post(
            f"{settings.API_V1_STR}/admin/my-club/courts",
            headers=admin_auth_headers,
            json=sample_court_data,
        )
        assert response.status_code == 404
        assert "does not own a club" in response.json()["detail"]

    def test_update_owned_club_court_success(
        self,
        client: TestClient,
        club_admin_auth_headers: dict,
        test_club: models.Club,
        test_court: models.Court,
    ):
        """Test successfully updating a court for owned club."""
        update_data = {
            "name": "Updated Court Name",
            "description": "Updated description",
        }
        response = client.put(
            f"{settings.API_V1_STR}/admin/my-club/courts/{test_court.id}",
            headers=club_admin_auth_headers,
            json=update_data,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Court Name"
        assert data["description"] == "Updated description"

    def test_update_owned_club_court_no_club(
        self, client: TestClient, admin_auth_headers: dict
    ):
        """Test updating a court when admin doesn't own a club."""
        update_data = {"name": "Updated Court Name"}
        response = client.put(
            f"{settings.API_V1_STR}/admin/my-club/courts/1",
            headers=admin_auth_headers,
            json=update_data,
        )
        assert response.status_code == 404
        assert "does not own a club" in response.json()["detail"]

    def test_update_owned_club_court_not_found(
        self, client: TestClient, club_admin_auth_headers: dict, test_club: models.Club
    ):
        """Test updating non-existent court."""
        update_data = {"name": "Updated Court Name"}
        response = client.put(
            f"{settings.API_V1_STR}/admin/my-club/courts/99999",
            headers=club_admin_auth_headers,
            json=update_data,
        )
        assert response.status_code == 404
        assert (
            "Court not found or not owned by the admin's club"
            in response.json()["detail"]
        )

    def test_read_owned_club_court_success(
        self,
        client: TestClient,
        club_admin_auth_headers: dict,
        test_club: models.Club,
        test_court: models.Court,
    ):
        """Test successfully reading a specific court for owned club."""
        response = client.get(
            f"{settings.API_V1_STR}/admin/my-club/courts/{test_court.id}",
            headers=club_admin_auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_court.id
        assert data["name"] == test_court.name

    def test_read_owned_club_court_no_club(
        self, client: TestClient, admin_auth_headers: dict
    ):
        """Test reading a court when admin doesn't own a club."""
        response = client.get(
            f"{settings.API_V1_STR}/admin/my-club/courts/1", headers=admin_auth_headers
        )
        assert response.status_code == 404
        assert "does not own a club" in response.json()["detail"]

    def test_read_owned_club_court_not_found(
        self, client: TestClient, club_admin_auth_headers: dict, test_club: models.Club
    ):
        """Test reading non-existent court."""
        response = client.get(
            f"{settings.API_V1_STR}/admin/my-club/courts/99999",
            headers=club_admin_auth_headers,
        )
        assert response.status_code == 404
        assert (
            "Court not found or not owned by the admin's club"
            in response.json()["detail"]
        )

    def test_delete_owned_club_court_success(
        self,
        client: TestClient,
        club_admin_auth_headers: dict,
        test_club: models.Club,
        test_court: models.Court,
    ):
        """Test successfully deleting a court for owned club."""
        response = client.delete(
            f"{settings.API_V1_STR}/admin/my-club/courts/{test_court.id}",
            headers=club_admin_auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_court.id

    def test_delete_owned_club_court_no_club(
        self, client: TestClient, admin_auth_headers: dict
    ):
        """Test deleting a court when admin doesn't own a club."""
        response = client.delete(
            f"{settings.API_V1_STR}/admin/my-club/courts/1", headers=admin_auth_headers
        )
        assert response.status_code == 404
        assert "does not own a club" in response.json()["detail"]

    def test_delete_owned_club_court_not_found(
        self, client: TestClient, club_admin_auth_headers: dict, test_club: models.Club
    ):
        """Test deleting non-existent court."""
        response = client.delete(
            f"{settings.API_V1_STR}/admin/my-club/courts/99999",
            headers=club_admin_auth_headers,
        )
        assert response.status_code == 404
        assert (
            "Court not found or not owned by the admin's club"
            in response.json()["detail"]
        )

    def test_read_owned_club_bookings_success(
        self,
        client: TestClient,
        club_admin_auth_headers: dict,
        test_club: models.Club,
        test_booking: models.Booking,
    ):
        """Test successfully reading owned club bookings."""
        response = client.get(
            f"{settings.API_V1_STR}/admin/my-club/bookings",
            headers=club_admin_auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["id"] == test_booking.id

    def test_read_owned_club_bookings_no_club(
        self, client: TestClient, admin_auth_headers: dict
    ):
        """Test reading owned club bookings when admin doesn't own a club."""
        response = client.get(
            f"{settings.API_V1_STR}/admin/my-club/bookings", headers=admin_auth_headers
        )
        assert response.status_code == 404
        assert "does not own a club" in response.json()["detail"]

    def test_read_owned_club_bookings_with_filters(
        self,
        client: TestClient,
        club_admin_auth_headers: dict,
        test_club: models.Club,
        test_booking: models.Booking,
    ):
        """Test reading owned club bookings with filters."""
        response = client.get(
            f"{settings.API_V1_STR}/admin/my-club/bookings",
            headers=club_admin_auth_headers,
            params={
                "start_date": date.today().isoformat(),
                "end_date": date.today().isoformat(),
                "skip": 0,
                "limit": 10,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_read_club_bookings_success(
        self,
        client: TestClient,
        club_admin_auth_headers: dict,
        test_club: models.Club,
        test_booking: models.Booking,
    ):
        """Test successfully reading club bookings."""
        response = client.get(
            f"{settings.API_V1_STR}/admin/club/{test_club.id}/bookings",
            headers=club_admin_auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["id"] == test_booking.id

    def test_read_club_bookings_with_filters(
        self, client: TestClient, club_admin_auth_headers: dict, test_club: models.Club
    ):
        """Test reading club bookings with filters."""
        response = client.get(
            f"{settings.API_V1_STR}/admin/club/{test_club.id}/bookings",
            headers=club_admin_auth_headers,
            params={
                "start_date": date.today().isoformat(),
                "end_date": date.today().isoformat(),
                "status": "CONFIRMED",
                "skip": 0,
                "limit": 10,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_read_game_for_booking_success(
        self,
        client: TestClient,
        club_admin_auth_headers: dict,
        test_booking: models.Booking,
        test_game: models.Game,
    ):
        """Test successfully reading game for booking."""
        response = client.get(
            f"{settings.API_V1_STR}/admin/bookings/{test_booking.id}/game",
            headers=club_admin_auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_game.id

    def test_read_game_for_booking_not_found(
        self, client: TestClient, club_admin_auth_headers: dict
    ):
        """Test reading game for non-existent booking."""
        response = client.get(
            f"{settings.API_V1_STR}/admin/bookings/99999/game",
            headers=club_admin_auth_headers,
        )
        assert response.status_code == 404
        assert "Game not found for this booking" in response.json()["detail"]

    @patch("app.services.file_service.save_club_picture")
    def test_upload_club_profile_picture_success(
        self,
        mock_save_picture,
        client: TestClient,
        club_admin_auth_headers: dict,
        test_club: models.Club,
    ):
        """Test successfully uploading club profile picture."""
        mock_save_picture.return_value = "https://example.com/picture.jpg"

        # Create a mock file
        files = {"file": ("test.jpg", b"fake image content", "image/jpeg")}

        response = client.post(
            f"{settings.API_V1_STR}/admin/my-club/profile-picture",
            headers=club_admin_auth_headers,
            files=files,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["image_url"] == "https://example.com/picture.jpg"

    def test_upload_club_profile_picture_no_club(
        self, client: TestClient, admin_auth_headers: dict
    ):
        """Test uploading club profile picture when admin doesn't own a club."""
        files = {"file": ("test.jpg", b"fake image content", "image/jpeg")}

        response = client.post(
            f"{settings.API_V1_STR}/admin/my-club/profile-picture",
            headers=admin_auth_headers,
            files=files,
        )
        assert response.status_code == 404
        assert "does not own a club" in response.json()["detail"]

    def test_upload_club_profile_picture_invalid_file_type(
        self, client: TestClient, club_admin_auth_headers: dict, test_club: models.Club
    ):
        """Test uploading invalid file type for club profile picture."""
        files = {"file": ("test.txt", b"fake text content", "text/plain")}

        response = client.post(
            f"{settings.API_V1_STR}/admin/my-club/profile-picture",
            headers=club_admin_auth_headers,
            files=files,
        )
        assert response.status_code == 400
        assert "Invalid file type" in response.json()["detail"]

    @patch("app.services.file_service.upload_file")
    def test_create_my_club_success(
        self,
        mock_upload_file,
        client: TestClient,
        admin_auth_headers: dict,
        db_session: Session,
    ):
        """Test successfully creating my club."""
        mock_upload_file.return_value = "https://example.com/club-image.jpg"

        form_data = {
            "name": "New Club",
            "description": "A new club for testing",
            "address": "789 New Ave",
            "city": "New City",
            "postal_code": "11111",
            "phone": "555-0789",
            "email": "new@club.com",
            "opening_time": "08:00",
            "closing_time": "22:00",
            "amenities": "WiFi, Parking",
        }

        files = {"image_file": ("club.jpg", b"fake image content", "image/jpeg")}

        response = client.post(
            f"{settings.API_V1_STR}/admin/my-club",
            headers=admin_auth_headers,
            data=form_data,
            files=files,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Club"
        assert data["image_url"] == "https://example.com/club-image.jpg"

    def test_create_my_club_already_owns_club(
        self, client: TestClient, club_admin_auth_headers: dict, test_club: models.Club
    ):
        """Test creating my club when admin already owns a club."""
        form_data = {"name": "Another Club", "description": "Another club for testing"}

        response = client.post(
            f"{settings.API_V1_STR}/admin/my-club",
            headers=club_admin_auth_headers,
            data=form_data,
        )
        assert response.status_code == 400
        assert "already owns a club" in response.json()["detail"]

    def test_create_my_club_without_image(
        self, client: TestClient, admin_auth_headers: dict
    ):
        """Test creating my club without image file."""
        form_data = {
            "name": "Club Without Image",
            "description": "A club without image for testing",
        }

        response = client.post(
            f"{settings.API_V1_STR}/admin/my-club",
            headers=admin_auth_headers,
            data=form_data,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Club Without Image"
        assert data["image_url"] is None

    def test_get_dashboard_summary_success(
        self, client: TestClient, club_admin_auth_headers: dict, test_club: models.Club
    ):
        """Test successfully getting dashboard summary."""
        response = client.get(
            f"{settings.API_V1_STR}/admin/club/{test_club.id}/dashboard-summary",
            headers=club_admin_auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_bookings_today" in data
        assert "occupancy_rate_percent" in data
        assert "recent_activity" in data

    def test_get_dashboard_summary_with_date(
        self, client: TestClient, club_admin_auth_headers: dict, test_club: models.Club
    ):
        """Test getting dashboard summary with specific date."""
        response = client.get(
            f"{settings.API_V1_STR}/admin/club/{test_club.id}/dashboard-summary",
            headers=club_admin_auth_headers,
            params={"date": date.today().isoformat()},
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_bookings_today" in data
        assert "occupancy_rate_percent" in data
        assert "recent_activity" in data

    def test_pagination_limits(
        self, client: TestClient, club_admin_auth_headers: dict, test_club: models.Club
    ):
        """Test pagination limits for bookings endpoint."""
        response = client.get(
            f"{settings.API_V1_STR}/admin/club/{test_club.id}/bookings",
            headers=club_admin_auth_headers,
            params={"skip": 0, "limit": 5},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5

    def test_authorization_boundary_cases(
        self, client: TestClient, player_auth_headers: dict, test_club: models.Club
    ):
        """Test authorization boundary cases."""
        # Player trying to access admin endpoints
        endpoints = [
            f"/admin/club/{test_club.id}",
            f"/admin/club/{test_club.id}/courts",
            f"/admin/club/{test_club.id}/bookings",
            "/admin/my-club",
            "/admin/my-club/courts",
        ]

        for endpoint in endpoints:
            response = client.get(
                f"{settings.API_V1_STR}{endpoint}", headers=player_auth_headers
            )
            assert (
                response.status_code == 403
            ), f"Endpoint {endpoint} should deny access to players"

    def test_error_handling_edge_cases(
        self, client: TestClient, club_admin_auth_headers: dict
    ):
        """Test error handling for edge cases."""
        # Test with malformed JSON
        response = client.put(
            f"{settings.API_V1_STR}/admin/club/1",
            headers=club_admin_auth_headers,
            data="invalid json",
        )
        assert response.status_code == 422

        # Test with missing required fields
        response = client.post(
            f"{settings.API_V1_STR}/admin/my-club/courts",
            headers=club_admin_auth_headers,
            json={},
        )
        assert response.status_code == 422
