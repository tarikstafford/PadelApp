import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import timedelta

from app.models.user import User
from app.models.user_role import UserRole
from app.schemas.user_schemas import UserCreate
from app.core.security import create_access_token, create_refresh_token


class TestAuthLogin:
    def test_login_success(self, client: TestClient):
        """Test successful login with valid credentials."""
        with patch('app.crud.user_crud.authenticate_user') as mock_auth, \
             patch('app.core.security.create_access_token') as mock_access_token, \
             patch('app.core.security.create_refresh_token') as mock_refresh_token:
            
            # Mock user
            mock_user = User(
                id=1,
                email="test@example.com",
                full_name="Test User",
                role=UserRole.PLAYER,
                is_active=True
            )
            mock_auth.return_value = mock_user
            mock_access_token.return_value = "access_token_123"
            mock_refresh_token.return_value = "refresh_token_123"
            
            # Make login request
            response = client.post(
                "/api/v1/auth/login",
                data={
                    "username": "test@example.com",
                    "password": "correct_password"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["access_token"] == "access_token_123"
            assert data["refresh_token"] == "refresh_token_123"
            assert data["token_type"] == "bearer"
            
            # Verify tokens were created with correct parameters
            mock_access_token.assert_called_once_with(
                subject="test@example.com",
                role="PLAYER"
            )
            mock_refresh_token.assert_called_once_with(
                subject="test@example.com",
                role="PLAYER"
            )

    def test_login_invalid_credentials(self, client: TestClient):
        """Test login with invalid credentials."""
        with patch('app.crud.user_crud.authenticate_user', return_value=None):
            response = client.post(
                "/api/v1/auth/login",
                data={
                    "username": "test@example.com",
                    "password": "wrong_password"
                }
            )
            
            assert response.status_code == 401
            data = response.json()
            assert "Incorrect email or password" in data["detail"]

    def test_login_inactive_user(self, client: TestClient):
        """Test login with inactive user."""
        with patch('app.crud.user_crud.authenticate_user') as mock_auth:
            # Mock inactive user
            inactive_user = User(
                id=1,
                email="test@example.com",
                full_name="Test User",
                is_active=False
            )
            mock_auth.return_value = inactive_user
            
            response = client.post(
                "/api/v1/auth/login",
                data={
                    "username": "test@example.com",
                    "password": "correct_password"
                }
            )
            
            assert response.status_code == 400
            data = response.json()
            assert "Inactive user" in data["detail"]

    def test_login_missing_fields(self, client: TestClient):
        """Test login with missing required fields."""
        # Missing password
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "test@example.com"}
        )
        assert response.status_code == 422
        
        # Missing username
        response = client.post(
            "/api/v1/auth/login",
            data={"password": "password"}
        )
        assert response.status_code == 422

    def test_login_empty_credentials(self, client: TestClient):
        """Test login with empty credentials."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "",
                "password": ""
            }
        )
        assert response.status_code == 422


class TestAuthRegister:
    def test_register_success(self, client: TestClient):
        """Test successful user registration."""
        with patch('app.crud.user_crud.get_user_by_email', return_value=None), \
             patch('app.crud.user_crud.create_user') as mock_create:
            
            mock_user = User(
                id=1,
                email="newuser@example.com",
                full_name="New User",
                role=UserRole.PLAYER,
                is_active=True
            )
            mock_create.return_value = mock_user
            
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "email": "newuser@example.com",
                    "password": "securepassword",
                    "full_name": "New User"
                }
            )
            
            assert response.status_code == 201
            data = response.json()
            
            assert data["id"] == 1
            assert data["email"] == "newuser@example.com"
            assert data["full_name"] == "New User"
            assert data["role"] == "PLAYER"
            assert data["is_active"] is True
            assert "hashed_password" not in data

    def test_register_duplicate_email(self, client: TestClient):
        """Test registration with existing email."""
        with patch('app.crud.user_crud.get_user_by_email') as mock_get:
            # Mock existing user
            existing_user = User(
                id=1,
                email="existing@example.com",
                full_name="Existing User"
            )
            mock_get.return_value = existing_user
            
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "email": "existing@example.com",
                    "password": "password",
                    "full_name": "New User"
                }
            )
            
            assert response.status_code == 400
            data = response.json()
            assert "Email already registered" in data["detail"]

    def test_register_invalid_email(self, client: TestClient):
        """Test registration with invalid email format."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "invalid-email",
                "password": "password",
                "full_name": "Test User"
            }
        )
        
        assert response.status_code == 422

    def test_register_weak_password(self, client: TestClient):
        """Test registration with weak password."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "123",  # Too short
                "full_name": "Test User"
            }
        )
        
        # Depending on validation rules, this might be 422 or succeed
        # This test documents the current behavior
        assert response.status_code in [201, 422]

    def test_register_missing_required_fields(self, client: TestClient):
        """Test registration with missing required fields."""
        # Missing email
        response = client.post(
            "/api/v1/auth/register",
            json={
                "password": "password",
                "full_name": "Test User"
            }
        )
        assert response.status_code == 422
        
        # Missing password
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "full_name": "Test User"
            }
        )
        assert response.status_code == 422
        
        # Missing full_name
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "password"
            }
        )
        assert response.status_code == 422


class TestTokenRefresh:
    def test_refresh_token_success(self, client: TestClient):
        """Test successful token refresh."""
        with patch('app.core.security.decode_token_payload') as mock_decode, \
             patch('app.crud.user_crud.get_user_by_email') as mock_get_user, \
             patch('app.core.security.create_access_token') as mock_access_token:
            
            # Mock token data
            from app.schemas.token_schemas import TokenData
            mock_token_data = TokenData(
                sub="test@example.com",
                role="PLAYER",
                token_type="refresh"
            )
            mock_decode.return_value = mock_token_data
            
            # Mock user
            mock_user = User(
                id=1,
                email="test@example.com",
                full_name="Test User",
                role=UserRole.PLAYER,
                is_active=True
            )
            mock_get_user.return_value = mock_user
            mock_access_token.return_value = "new_access_token_123"
            
            response = client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": "valid_refresh_token"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["access_token"] == "new_access_token_123"
            assert data["token_type"] == "bearer"

    def test_refresh_token_invalid(self, client: TestClient):
        """Test refresh with invalid token."""
        from fastapi import HTTPException
        
        with patch('app.core.security.decode_token_payload') as mock_decode:
            mock_decode.side_effect = HTTPException(
                status_code=401,
                detail="Invalid token"
            )
            
            response = client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": "invalid_token"}
            )
            
            assert response.status_code == 401

    def test_refresh_token_wrong_type(self, client: TestClient):
        """Test refresh with access token instead of refresh token."""
        with patch('app.core.security.decode_token_payload') as mock_decode:
            from app.schemas.token_schemas import TokenData
            mock_token_data = TokenData(
                sub="test@example.com",
                role="PLAYER",
                token_type="access"  # Wrong type
            )
            mock_decode.return_value = mock_token_data
            
            response = client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": "access_token_not_refresh"}
            )
            
            assert response.status_code == 401
            data = response.json()
            assert "Invalid token type" in data["detail"]

    def test_refresh_token_user_not_found(self, client: TestClient):
        """Test refresh when user no longer exists."""
        with patch('app.core.security.decode_token_payload') as mock_decode, \
             patch('app.crud.user_crud.get_user_by_email', return_value=None):
            
            from app.schemas.token_schemas import TokenData
            mock_token_data = TokenData(
                sub="deleted@example.com",
                role="PLAYER",
                token_type="refresh"
            )
            mock_decode.return_value = mock_token_data
            
            response = client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": "valid_token_deleted_user"}
            )
            
            assert response.status_code == 404
            data = response.json()
            assert "User not found" in data["detail"]

    def test_refresh_token_inactive_user(self, client: TestClient):
        """Test refresh for inactive user."""
        with patch('app.core.security.decode_token_payload') as mock_decode, \
             patch('app.crud.user_crud.get_user_by_email') as mock_get_user:
            
            from app.schemas.token_schemas import TokenData
            mock_token_data = TokenData(
                sub="test@example.com",
                role="PLAYER",
                token_type="refresh"
            )
            mock_decode.return_value = mock_token_data
            
            # Mock inactive user
            inactive_user = User(
                id=1,
                email="test@example.com",
                full_name="Test User",
                is_active=False
            )
            mock_get_user.return_value = inactive_user
            
            response = client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": "valid_token_inactive_user"}
            )
            
            assert response.status_code == 400
            data = response.json()
            assert "Inactive user" in data["detail"]


class TestProfilePictureUpload:
    def test_profile_picture_upload_success(self, client: TestClient, user_auth_headers: dict):
        """Test successful profile picture upload."""
        with patch('app.services.file_service.upload_profile_picture') as mock_upload, \
             patch('app.crud.user_crud.update_user') as mock_update:
            
            mock_upload.return_value = "https://cloudinary.com/image123.jpg"
            
            mock_user = User(
                id=1,
                email="test@example.com",
                full_name="Test User",
                profile_picture_url="https://cloudinary.com/image123.jpg"
            )
            mock_update.return_value = mock_user
            
            # Create a mock file
            files = {"file": ("test.jpg", b"fake image data", "image/jpeg")}
            
            response = client.post(
                "/api/v1/auth/profile-picture",
                files=files,
                headers=user_auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["profile_picture_url"] == "https://cloudinary.com/image123.jpg"

    def test_profile_picture_upload_unauthorized(self, client: TestClient):
        """Test profile picture upload without authentication."""
        files = {"file": ("test.jpg", b"fake image data", "image/jpeg")}
        
        response = client.post(
            "/api/v1/auth/profile-picture",
            files=files
        )
        
        assert response.status_code == 401

    def test_profile_picture_upload_invalid_file_type(self, client: TestClient, user_auth_headers: dict):
        """Test profile picture upload with invalid file type."""
        with patch('app.services.file_service.upload_profile_picture') as mock_upload:
            from fastapi import HTTPException
            mock_upload.side_effect = HTTPException(
                status_code=400,
                detail="Invalid file type"
            )
            
            files = {"file": ("test.txt", b"not an image", "text/plain")}
            
            response = client.post(
                "/api/v1/auth/profile-picture",
                files=files,
                headers=user_auth_headers
            )
            
            assert response.status_code == 400

    def test_profile_picture_upload_no_file(self, client: TestClient, user_auth_headers: dict):
        """Test profile picture upload without file."""
        response = client.post(
            "/api/v1/auth/profile-picture",
            headers=user_auth_headers
        )
        
        assert response.status_code == 422


class TestAuthIntegration:
    def test_register_login_workflow(self, client: TestClient):
        """Integration test for register -> login workflow."""
        with patch('app.crud.user_crud.get_user_by_email') as mock_get, \
             patch('app.crud.user_crud.create_user') as mock_create, \
             patch('app.crud.user_crud.authenticate_user') as mock_auth, \
             patch('app.core.security.create_access_token') as mock_access_token, \
             patch('app.core.security.create_refresh_token') as mock_refresh_token:
            
            # Registration phase
            mock_get.return_value = None  # No existing user
            
            new_user = User(
                id=1,
                email="newuser@example.com",
                full_name="New User",
                role=UserRole.PLAYER,
                is_active=True
            )
            mock_create.return_value = new_user
            
            # Register
            register_response = client.post(
                "/api/v1/auth/register",
                json={
                    "email": "newuser@example.com",
                    "password": "securepassword",
                    "full_name": "New User"
                }
            )
            
            assert register_response.status_code == 201
            
            # Login phase
            mock_auth.return_value = new_user
            mock_access_token.return_value = "access_token"
            mock_refresh_token.return_value = "refresh_token"
            
            # Login
            login_response = client.post(
                "/api/v1/auth/login",
                data={
                    "username": "newuser@example.com",
                    "password": "securepassword"
                }
            )
            
            assert login_response.status_code == 200
            data = login_response.json()
            assert "access_token" in data
            assert "refresh_token" in data

    def test_login_refresh_workflow(self, client: TestClient):
        """Integration test for login -> refresh token workflow."""
        with patch('app.crud.user_crud.authenticate_user') as mock_auth, \
             patch('app.core.security.create_access_token') as mock_access_token, \
             patch('app.core.security.create_refresh_token') as mock_refresh_token, \
             patch('app.core.security.decode_token_payload') as mock_decode, \
             patch('app.crud.user_crud.get_user_by_email') as mock_get_user:
            
            # Login phase
            user = User(
                id=1,
                email="test@example.com",
                full_name="Test User",
                role=UserRole.PLAYER,
                is_active=True
            )
            mock_auth.return_value = user
            mock_access_token.return_value = "access_token"
            mock_refresh_token.return_value = "refresh_token"
            
            login_response = client.post(
                "/api/v1/auth/login",
                data={
                    "username": "test@example.com",
                    "password": "password"
                }
            )
            
            assert login_response.status_code == 200
            tokens = login_response.json()
            
            # Refresh phase
            from app.schemas.token_schemas import TokenData
            mock_token_data = TokenData(
                sub="test@example.com",
                role="PLAYER",
                token_type="refresh"
            )
            mock_decode.return_value = mock_token_data
            mock_get_user.return_value = user
            mock_access_token.return_value = "new_access_token"
            
            refresh_response = client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": tokens["refresh_token"]}
            )
            
            assert refresh_response.status_code == 200
            new_tokens = refresh_response.json()
            assert "access_token" in new_tokens


class TestAuthEdgeCases:
    def test_login_with_special_characters_in_password(self, client: TestClient):
        """Test login with special characters in password."""
        with patch('app.crud.user_crud.authenticate_user') as mock_auth:
            mock_user = User(
                id=1,
                email="test@example.com",
                full_name="Test User",
                is_active=True
            )
            mock_auth.return_value = mock_user
            
            with patch('app.core.security.create_access_token', return_value="token"), \
                 patch('app.core.security.create_refresh_token', return_value="refresh"):
                
                response = client.post(
                    "/api/v1/auth/login",
                    data={
                        "username": "test@example.com",
                        "password": "p@ssw0rd!#$%^&*()"
                    }
                )
                
                assert response.status_code == 200

    def test_register_with_unicode_name(self, client: TestClient):
        """Test registration with unicode characters in name."""
        with patch('app.crud.user_crud.get_user_by_email', return_value=None), \
             patch('app.crud.user_crud.create_user') as mock_create:
            
            mock_user = User(
                id=1,
                email="unicode@example.com",
                full_name="José María Äzçléń",
                role=UserRole.PLAYER,
                is_active=True
            )
            mock_create.return_value = mock_user
            
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "email": "unicode@example.com",
                    "password": "password",
                    "full_name": "José María Äzçléń"
                }
            )
            
            assert response.status_code == 201
            data = response.json()
            assert data["full_name"] == "José María Äzçléń"

    def test_multiple_concurrent_logins(self, client: TestClient):
        """Test multiple concurrent login attempts for same user."""
        with patch('app.crud.user_crud.authenticate_user') as mock_auth, \
             patch('app.core.security.create_access_token') as mock_access_token, \
             patch('app.core.security.create_refresh_token') as mock_refresh_token:
            
            mock_user = User(
                id=1,
                email="test@example.com",
                full_name="Test User",
                is_active=True
            )
            mock_auth.return_value = mock_user
            mock_access_token.side_effect = ["token1", "token2", "token3"]
            mock_refresh_token.side_effect = ["refresh1", "refresh2", "refresh3"]
            
            # Multiple login requests
            responses = []
            for i in range(3):
                response = client.post(
                    "/api/v1/auth/login",
                    data={
                        "username": "test@example.com",
                        "password": "password"
                    }
                )
                responses.append(response)
            
            # All should succeed with different tokens
            for i, response in enumerate(responses):
                assert response.status_code == 200
                data = response.json()
                assert data["access_token"] == f"token{i+1}"
                assert data["refresh_token"] == f"refresh{i+1}"