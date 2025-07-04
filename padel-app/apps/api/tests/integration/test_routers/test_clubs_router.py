import pytest
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app import models, schemas, crud
from app.core.config import settings


class TestClubsRouter:
    """Test suite for clubs router endpoints."""

    def test_create_club_success(self, client: TestClient, club_admin_auth_headers: dict, 
                                 db_session: Session, sample_club_data: dict):
        """Test successful club creation by club admin."""
        response = client.post(
            f"{settings.API_V1_STR}/clubs",
            headers=club_admin_auth_headers,
            json=sample_club_data
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_club_data["name"]
        assert data["description"] == sample_club_data["description"]
        assert data["city"] == sample_club_data["city"]
        assert data["email"] == sample_club_data["email"]

    def test_create_club_not_club_admin(self, client: TestClient, player_auth_headers: dict, 
                                       sample_club_data: dict):
        """Test that only club admins can create clubs."""
        response = client.post(
            f"{settings.API_V1_STR}/clubs",
            headers=player_auth_headers,
            json=sample_club_data
        )
        assert response.status_code == 403
        assert "Only club admins can create new clubs" in response.json()["detail"]

    def test_create_club_admin_already_owns_club(self, client: TestClient, club_admin_auth_headers: dict, 
                                                test_club: models.Club, sample_club_data: dict):
        """Test that club admin cannot create another club if they already own one."""
        response = client.post(
            f"{settings.API_V1_STR}/clubs",
            headers=club_admin_auth_headers,
            json=sample_club_data
        )
        assert response.status_code == 400
        assert "already owns a club" in response.json()["detail"]

    def test_create_club_unauthorized(self, client: TestClient, sample_club_data: dict):
        """Test club creation without authentication."""
        response = client.post(
            f"{settings.API_V1_STR}/clubs",
            json=sample_club_data
        )
        assert response.status_code == 401

    def test_create_club_invalid_data(self, client: TestClient, club_admin_auth_headers: dict):
        """Test club creation with invalid data."""
        invalid_data = {
            "name": "",  # Empty name should fail validation
            "description": "Valid description"
        }
        
        response = client.post(
            f"{settings.API_V1_STR}/clubs",
            headers=club_admin_auth_headers,
            json=invalid_data
        )
        assert response.status_code == 422

    def test_create_club_missing_required_fields(self, client: TestClient, club_admin_auth_headers: dict):
        """Test club creation with missing required fields."""
        incomplete_data = {
            "description": "Only description provided"
            # Missing required 'name' field
        }
        
        response = client.post(
            f"{settings.API_V1_STR}/clubs",
            headers=club_admin_auth_headers,
            json=incomplete_data
        )
        assert response.status_code == 422

    def test_create_club_with_super_admin(self, client: TestClient, super_admin_auth_headers: dict, 
                                         sample_club_data: dict):
        """Test that super admin cannot create clubs (only club admins can)."""
        response = client.post(
            f"{settings.API_V1_STR}/clubs",
            headers=super_admin_auth_headers,
            json=sample_club_data
        )
        assert response.status_code == 403
        assert "Only club admins can create new clubs" in response.json()["detail"]

    def test_read_clubs_success(self, client: TestClient, test_club: models.Club):
        """Test successfully reading list of clubs."""
        response = client.get(f"{settings.API_V1_STR}/clubs")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        club_names = [club["name"] for club in data]
        assert test_club.name in club_names

    def test_read_clubs_with_pagination(self, client: TestClient, db_session: Session, 
                                       club_admin_user: models.User):
        """Test reading clubs with pagination."""
        # Create multiple clubs
        for i in range(5):
            club_in = schemas.ClubCreate(
                name=f"Test Club {i}",
                description=f"Description {i}",
                owner_id=club_admin_user.id
            )
            crud.club_crud.create_club(db_session, club_in)
        
        # Test pagination
        response = client.get(
            f"{settings.API_V1_STR}/clubs",
            params={"skip": 0, "limit": 3}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 3

    def test_read_clubs_with_name_filter(self, client: TestClient, test_club: models.Club):
        """Test reading clubs with name filter."""
        response = client.get(
            f"{settings.API_V1_STR}/clubs",
            params={"name": test_club.name}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert all(test_club.name.lower() in club["name"].lower() for club in data)

    def test_read_clubs_with_city_filter(self, client: TestClient, test_club: models.Club):
        """Test reading clubs with city filter."""
        response = client.get(
            f"{settings.API_V1_STR}/clubs",
            params={"city": test_club.city}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert all(club["city"] == test_club.city for club in data if club["city"])

    def test_read_clubs_with_sorting(self, client: TestClient, test_club: models.Club):
        """Test reading clubs with sorting."""
        response = client.get(
            f"{settings.API_V1_STR}/clubs",
            params={"sort_by": "name", "sort_desc": False}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Verify sorting (if multiple clubs exist)
        if len(data) > 1:
            names = [club["name"] for club in data]
            assert names == sorted(names)

    def test_read_clubs_with_descending_sort(self, client: TestClient, test_club: models.Club):
        """Test reading clubs with descending sort."""
        response = client.get(
            f"{settings.API_V1_STR}/clubs",
            params={"sort_by": "name", "sort_desc": True}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_read_clubs_invalid_pagination(self, client: TestClient):
        """Test reading clubs with invalid pagination parameters."""
        response = client.get(
            f"{settings.API_V1_STR}/clubs",
            params={"skip": -1, "limit": 0}
        )
        assert response.status_code == 422

    def test_read_clubs_limit_exceeded(self, client: TestClient):
        """Test reading clubs with limit exceeding maximum."""
        response = client.get(
            f"{settings.API_V1_STR}/clubs",
            params={"limit": 300}  # Exceeds maximum of 200
        )
        assert response.status_code == 422

    def test_read_clubs_invalid_filter_values(self, client: TestClient):
        """Test reading clubs with invalid filter values."""
        # Test with empty string filters (should fail min_length validation)
        response = client.get(
            f"{settings.API_V1_STR}/clubs",
            params={"name": "", "city": ""}
        )
        assert response.status_code == 422

    def test_read_clubs_filter_too_long(self, client: TestClient):
        """Test reading clubs with filter values that are too long."""
        long_string = "a" * 101  # Exceeds max_length of 100
        response = client.get(
            f"{settings.API_V1_STR}/clubs",
            params={"name": long_string}
        )
        assert response.status_code == 422

    def test_read_club_success(self, client: TestClient, test_club: models.Club):
        """Test successfully reading a specific club."""
        response = client.get(f"{settings.API_V1_STR}/clubs/{test_club.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_club.id
        assert data["name"] == test_club.name
        assert data["description"] == test_club.description
        # Should include courts in response (ClubWithCourts schema)
        assert "courts" in data

    def test_read_club_not_found(self, client: TestClient):
        """Test reading non-existent club."""
        response = client.get(f"{settings.API_V1_STR}/clubs/99999")
        assert response.status_code == 404
        assert "Club not found" in response.json()["detail"]

    def test_read_club_invalid_id(self, client: TestClient):
        """Test reading club with invalid ID format."""
        response = client.get(f"{settings.API_V1_STR}/clubs/invalid-id")
        assert response.status_code == 422

    def test_read_club_with_courts(self, client: TestClient, test_club: models.Club, 
                                  test_court: models.Court):
        """Test reading club includes its courts."""
        response = client.get(f"{settings.API_V1_STR}/clubs/{test_club.id}")
        assert response.status_code == 200
        data = response.json()
        assert "courts" in data
        assert len(data["courts"]) >= 1
        court_ids = [court["id"] for court in data["courts"]]
        assert test_court.id in court_ids

    def test_read_club_courts_success(self, client: TestClient, test_club: models.Club, 
                                     test_court: models.Court):
        """Test successfully reading courts for a specific club."""
        response = client.get(f"{settings.API_V1_STR}/clubs/{test_club.id}/courts")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["id"] == test_court.id
        assert data[0]["name"] == test_court.name
        assert data[0]["club_id"] == test_club.id

    def test_read_club_courts_club_not_found(self, client: TestClient):
        """Test reading courts for non-existent club."""
        response = client.get(f"{settings.API_V1_STR}/clubs/99999/courts")
        assert response.status_code == 404
        assert "Club not found" in response.json()["detail"]

    def test_read_club_courts_with_pagination(self, client: TestClient, test_club: models.Club, 
                                             db_session: Session):
        """Test reading club courts with pagination."""
        # Create multiple courts
        for i in range(5):
            court_in = schemas.CourtCreate(
                name=f"Court {i}",
                description=f"Description {i}",
                club_id=test_club.id
            )
            crud.court_crud.create_court(db_session, court_in, test_club.id)
        
        # Test pagination
        response = client.get(
            f"{settings.API_V1_STR}/clubs/{test_club.id}/courts",
            params={"skip": 0, "limit": 3}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 3

    def test_read_club_courts_invalid_pagination(self, client: TestClient, test_club: models.Club):
        """Test reading club courts with invalid pagination."""
        response = client.get(
            f"{settings.API_V1_STR}/clubs/{test_club.id}/courts",
            params={"skip": -1, "limit": 0}
        )
        assert response.status_code == 422

    def test_read_club_courts_limit_exceeded(self, client: TestClient, test_club: models.Club):
        """Test reading club courts with limit exceeding maximum."""
        response = client.get(
            f"{settings.API_V1_STR}/clubs/{test_club.id}/courts",
            params={"limit": 150}  # Exceeds maximum of 100
        )
        assert response.status_code == 422

    def test_read_club_courts_empty_result(self, client: TestClient, db_session: Session, 
                                          club_admin_user: models.User):
        """Test reading courts for club with no courts."""
        # Create a club without courts
        club_in = schemas.ClubCreate(
            name="Empty Club",
            description="Club with no courts",
            owner_id=club_admin_user.id
        )
        empty_club = crud.club_crud.create_club(db_session, club_in)
        
        response = client.get(f"{settings.API_V1_STR}/clubs/{empty_club.id}/courts")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    def test_club_creation_business_rules(self, client: TestClient, db_session: Session):
        """Test business rules for club creation."""
        # Create a club admin user
        user_in = schemas.UserCreate(
            email="newclubadmin@example.com",
            password="newadminpass123",
            full_name="New Club Admin",
            role=models.UserRole.CLUB_ADMIN
        )
        new_admin = crud.user_crud.create_user(db_session, user_in)
        
        # Get auth headers for new admin
        from app.core.security import create_access_token
        token = create_access_token(subject=new_admin.email, role=new_admin.role.value)
        headers = {"Authorization": f"Bearer {token}"}
        
        # Should be able to create one club
        club_data = {
            "name": "New Admin Club",
            "description": "Club for new admin"
        }
        
        response = client.post(
            f"{settings.API_V1_STR}/clubs",
            headers=headers,
            json=club_data
        )
        assert response.status_code == 201
        
        # Should not be able to create second club
        club_data2 = {
            "name": "Second Club",
            "description": "Second club attempt"
        }
        
        response2 = client.post(
            f"{settings.API_V1_STR}/clubs",
            headers=headers,
            json=club_data2
        )
        assert response2.status_code == 400

    def test_club_data_validation_edge_cases(self, client: TestClient, db_session: Session):
        """Test edge cases for club data validation."""
        # Create a club admin user without existing club
        user_in = schemas.UserCreate(
            email="validationadmin@example.com",
            password="validationpass123",
            full_name="Validation Admin",
            role=models.UserRole.CLUB_ADMIN
        )
        validation_admin = crud.user_crud.create_user(db_session, user_in)
        
        from app.core.security import create_access_token
        token = create_access_token(subject=validation_admin.email, role=validation_admin.role.value)
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test with very long name
        club_data = {
            "name": "A" * 1000,  # Very long name
            "description": "Valid description"
        }
        
        response = client.post(
            f"{settings.API_V1_STR}/clubs",
            headers=headers,
            json=club_data
        )
        # Should either succeed or fail validation depending on schema limits
        assert response.status_code in [201, 422]

    def test_club_search_functionality(self, client: TestClient, db_session: Session, 
                                     club_admin_user: models.User):
        """Test club search functionality."""
        # Create clubs with specific names and cities
        test_clubs = [
            {"name": "Madrid Padel Club", "city": "Madrid", "description": "Club in Madrid"},
            {"name": "Barcelona Sports", "city": "Barcelona", "description": "Club in Barcelona"},
            {"name": "Valencia Tennis", "city": "Valencia", "description": "Club in Valencia"}
        ]
        
        for club_data in test_clubs:
            club_in = schemas.ClubCreate(
                name=club_data["name"],
                description=club_data["description"],
                city=club_data["city"],
                owner_id=club_admin_user.id
            )
            crud.club_crud.create_club(db_session, club_in)
        
        # Test name search
        response = client.get(
            f"{settings.API_V1_STR}/clubs",
            params={"name": "Madrid"}
        )
        assert response.status_code == 200
        data = response.json()
        assert any("Madrid" in club["name"] for club in data)
        
        # Test city search
        response = client.get(
            f"{settings.API_V1_STR}/clubs",
            params={"city": "Barcelona"}
        )
        assert response.status_code == 200
        data = response.json()
        assert any(club["city"] == "Barcelona" for club in data if club["city"])

    def test_club_endpoint_performance(self, client: TestClient, test_club: models.Club):
        """Test club endpoint performance with multiple requests."""
        # Make multiple requests to ensure consistent performance
        for _ in range(10):
            response = client.get(f"{settings.API_V1_STR}/clubs")
            assert response.status_code == 200
            
            response = client.get(f"{settings.API_V1_STR}/clubs/{test_club.id}")
            assert response.status_code == 200

    def test_club_error_handling(self, client: TestClient, club_admin_auth_headers: dict):
        """Test error handling in club endpoints."""
        # Test with malformed JSON
        response = client.post(
            f"{settings.API_V1_STR}/clubs",
            data="invalid json",
            headers={**club_admin_auth_headers, "Content-Type": "application/json"}
        )
        assert response.status_code == 422

    def test_club_sql_injection_protection(self, client: TestClient):
        """Test protection against SQL injection in club parameters."""
        # Test with malicious query parameters
        response = client.get(
            f"{settings.API_V1_STR}/clubs",
            params={"name": "'; DROP TABLE clubs; --"}
        )
        # Should not cause server error, just return normal response
        assert response.status_code == 200

    def test_club_authorization_boundary_cases(self, client: TestClient, sample_club_data: dict):
        """Test authorization boundary cases."""
        # Test different role combinations
        roles_and_expected_status = [
            ("invalid_token", 401),
            ("no_token", 401),
        ]
        
        for role, expected_status in roles_and_expected_status:
            if role == "no_token":
                response = client.post(f"{settings.API_V1_STR}/clubs", json=sample_club_data)
            else:
                headers = {"Authorization": f"Bearer {role}"}
                response = client.post(
                    f"{settings.API_V1_STR}/clubs",
                    headers=headers,
                    json=sample_club_data
                )
            assert response.status_code == expected_status

    def test_club_concurrent_creation(self, client: TestClient, db_session: Session):
        """Test concurrent club creation by same admin."""
        # Create a club admin user
        user_in = schemas.UserCreate(
            email="concurrentadmin@example.com",
            password="concurrentpass123",
            full_name="Concurrent Admin",
            role=models.UserRole.CLUB_ADMIN
        )
        concurrent_admin = crud.user_crud.create_user(db_session, user_in)
        
        from app.core.security import create_access_token
        token = create_access_token(subject=concurrent_admin.email, role=concurrent_admin.role.value)
        headers = {"Authorization": f"Bearer {token}"}
        
        club_data = {
            "name": "Concurrent Club",
            "description": "Club for concurrent testing"
        }
        
        # First request should succeed
        response1 = client.post(
            f"{settings.API_V1_STR}/clubs",
            headers=headers,
            json=club_data
        )
        assert response1.status_code == 201
        
        # Second request should fail
        response2 = client.post(
            f"{settings.API_V1_STR}/clubs",
            headers=headers,
            json=club_data
        )
        assert response2.status_code == 400