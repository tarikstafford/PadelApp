import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from sqlalchemy.orm import Session
from jose import jwt

from app.core.security import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    create_refresh_token,
    decode_token_payload,
    get_current_user,
    get_current_active_user
)
from app.core.config import settings
from app.models.user import User
from app.schemas.token_schemas import TokenData


class TestPasswordHashing:
    def test_get_password_hash(self):
        password = "test_password"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")  # bcrypt hash prefix

    def test_verify_password_correct(self):
        password = "test_password"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        password = "test_password"
        wrong_password = "wrong_password"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_empty_strings(self):
        assert verify_password("", "") is False

    def test_hash_consistency(self):
        """Test that the same password produces different hashes due to salt."""
        password = "test_password"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        assert hash1 != hash2
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestTokenCreation:
    def test_create_access_token_default_expiry(self):
        subject = "test@example.com"
        token = create_access_token(subject)
        
        # Decode without verification to check contents
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        assert payload["sub"] == subject
        assert payload["token_type"] == "access"
        assert "exp" in payload
        assert "role" not in payload

    def test_create_access_token_with_role(self):
        subject = "test@example.com"
        role = "ADMIN"
        token = create_access_token(subject, role=role)
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        assert payload["sub"] == subject
        assert payload["role"] == role
        assert payload["token_type"] == "access"

    def test_create_access_token_custom_expiry(self):
        subject = "test@example.com"
        expires_delta = timedelta(hours=2)
        token = create_access_token(subject, expires_delta=expires_delta)
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Check that expiry is approximately 2 hours from now
        exp_timestamp = payload["exp"]
        expected_exp = datetime.now(timezone.utc) + expires_delta
        actual_exp = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        
        # Allow 1 minute difference for test execution time
        assert abs((actual_exp - expected_exp).total_seconds()) < 60

    def test_create_refresh_token_default_expiry(self):
        subject = "test@example.com"
        token = create_refresh_token(subject)
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        assert payload["sub"] == subject
        assert payload["token_type"] == "refresh"
        assert "exp" in payload

    def test_create_refresh_token_with_role(self):
        subject = "test@example.com"
        role = "PLAYER"
        token = create_refresh_token(subject, role=role)
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        assert payload["sub"] == subject
        assert payload["role"] == role
        assert payload["token_type"] == "refresh"


class TestTokenDecoding:
    def test_decode_token_payload_valid_access_token(self):
        subject = "test@example.com"
        role = "PLAYER"
        token = create_access_token(subject, role=role)
        
        token_data = decode_token_payload(token)
        
        assert token_data.sub == subject
        assert token_data.role == role
        assert token_data.token_type == "access"

    def test_decode_token_payload_valid_refresh_token(self):
        subject = "test@example.com"
        token = create_refresh_token(subject)
        
        token_data = decode_token_payload(token)
        
        assert token_data.sub == subject
        assert token_data.token_type == "refresh"

    def test_decode_token_payload_invalid_token(self):
        invalid_token = "invalid.token.here"
        
        with pytest.raises(HTTPException) as exc_info:
            decode_token_payload(invalid_token)
        
        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in exc_info.value.detail

    def test_decode_token_payload_expired_token(self):
        subject = "test@example.com"
        # Create token that expires in the past
        expires_delta = timedelta(seconds=-1)
        token = create_access_token(subject, expires_delta=expires_delta)
        
        with pytest.raises(HTTPException) as exc_info:
            decode_token_payload(token)
        
        assert exc_info.value.status_code == 401

    def test_decode_token_payload_malformed_no_subject(self):
        # Create token without subject
        payload = {
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
            "token_type": "access"
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        with pytest.raises(HTTPException) as exc_info:
            decode_token_payload(token)
        
        assert exc_info.value.status_code == 401
        assert "malformed token payload" in exc_info.value.detail

    def test_decode_token_payload_malformed_no_expiry(self):
        # Create token without expiry
        payload = {
            "sub": "test@example.com",
            "token_type": "access"
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        with pytest.raises(HTTPException) as exc_info:
            decode_token_payload(token)
        
        assert exc_info.value.status_code == 401
        assert "malformed token payload" in exc_info.value.detail


class TestGetCurrentUser:
    @pytest.mark.asyncio
    async def test_get_current_user_valid_token(self):
        # Mock database session
        mock_db = Mock(spec=Session)
        
        # Mock user
        mock_user = User(
            id=1,
            email="test@example.com",
            full_name="Test User",
            is_active=True
        )
        
        # Create valid token
        token = create_access_token("test@example.com")
        
        with patch('app.crud.user_crud.get_user_by_email', return_value=mock_user):
            user = await get_current_user(mock_db, token)
            
            assert user == mock_user

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self):
        mock_db = Mock(spec=Session)
        invalid_token = "invalid.token"
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_db, invalid_token)
        
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_refresh_token(self):
        mock_db = Mock(spec=Session)
        refresh_token = create_refresh_token("test@example.com")
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_db, refresh_token)
        
        assert exc_info.value.status_code == 401
        assert "Invalid token type" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_current_user_user_not_found(self):
        mock_db = Mock(spec=Session)
        token = create_access_token("nonexistent@example.com")
        
        with patch('app.crud.user_crud.get_user_by_email', return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(mock_db, token)
            
            assert exc_info.value.status_code == 404
            assert "User not found" in exc_info.value.detail


class TestGetCurrentActiveUser:
    @pytest.mark.asyncio
    async def test_get_current_active_user_active(self):
        active_user = User(
            id=1,
            email="test@example.com",
            full_name="Test User",
            is_active=True
        )
        
        user = await get_current_active_user(active_user)
        assert user == active_user

    @pytest.mark.asyncio
    async def test_get_current_active_user_inactive(self):
        inactive_user = User(
            id=1,
            email="test@example.com", 
            full_name="Test User",
            is_active=False
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_active_user(inactive_user)
        
        assert exc_info.value.status_code == 400
        assert "Inactive user" in exc_info.value.detail


class TestTokenIntegration:
    def test_access_token_roundtrip(self):
        """Test creating an access token and then decoding it."""
        subject = "test@example.com"
        role = "ADMIN"
        
        token = create_access_token(subject, role=role)
        token_data = decode_token_payload(token)
        
        assert token_data.sub == subject
        assert token_data.role == role
        assert token_data.token_type == "access"

    def test_refresh_token_roundtrip(self):
        """Test creating a refresh token and then decoding it."""
        subject = "test@example.com"
        
        token = create_refresh_token(subject)
        token_data = decode_token_payload(token)
        
        assert token_data.sub == subject
        assert token_data.token_type == "refresh"

    def test_different_tokens_for_same_user(self):
        """Test that different tokens are generated for the same user."""
        subject = "test@example.com"
        
        token1 = create_access_token(subject)
        token2 = create_access_token(subject)
        
        assert token1 != token2
        
        # Both should decode to the same subject
        token_data1 = decode_token_payload(token1)
        token_data2 = decode_token_payload(token2)
        
        assert token_data1.sub == token_data2.sub == subject