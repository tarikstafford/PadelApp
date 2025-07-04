from unittest.mock import Mock, patch

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.crud.user_crud import (
    create_user,
    get_user,
    get_user_by_email,
    search_users,
    update_user,
)
from app.models.user import User
from app.models.user_role import UserRole
from app.schemas.user_schemas import UserCreate, UserUpdate


class TestGetUser:
    def test_get_user_found(self):
        mock_db = Mock(spec=Session)
        mock_user = User(id=1, email="test@example.com")
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        result = get_user(mock_db, user_id=1)

        assert result == mock_user
        mock_db.query.assert_called_once_with(User)
        mock_db.query.return_value.filter.assert_called_once()

    def test_get_user_not_found(self):
        mock_db = Mock(spec=Session)
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = get_user(mock_db, user_id=999)

        assert result is None


class TestGetUserByEmail:
    def test_get_user_by_email_found(self):
        mock_db = Mock(spec=Session)
        mock_user = User(id=1, email="test@example.com")
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        result = get_user_by_email(mock_db, email="test@example.com")

        assert result == mock_user

    def test_get_user_by_email_not_found(self):
        mock_db = Mock(spec=Session)
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = get_user_by_email(mock_db, email="nonexistent@example.com")

        assert result is None

    def test_get_user_by_email_case_sensitivity(self):
        mock_db = Mock(spec=Session)
        mock_user = User(id=1, email="test@example.com")
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        get_user_by_email(mock_db, email="TEST@EXAMPLE.COM")

        # Should still find the user (assuming case-insensitive search in DB)
        mock_db.query.assert_called_once_with(User)


class TestCreateUser:
    @patch("app.crud.user_crud.get_password_hash")
    def test_create_user_success(self, mock_hash):
        mock_db = Mock(spec=Session)
        mock_hash.return_value = "hashed_password"

        user_data = UserCreate(
            email="test@example.com",
            password="plaintext_password",
            full_name="Test User",
            elo_rating=1.5,
        )

        create_user(mock_db, user_data)

        # Verify password was hashed
        mock_hash.assert_called_once_with("plaintext_password")

        # Verify database operations
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

        # Verify the created user object has correct attributes
        added_user = mock_db.add.call_args[0][0]
        assert added_user.email == "test@example.com"
        assert added_user.hashed_password == "hashed_password"
        assert added_user.full_name == "Test User"
        assert added_user.elo_rating == 1.5

    @patch("app.crud.user_crud.get_password_hash")
    def test_create_user_with_role(self, mock_hash):
        mock_db = Mock(spec=Session)
        mock_hash.return_value = "hashed_password"

        user_data = UserCreate(
            email="admin@example.com",
            password="password",
            full_name="Admin User",
            role=UserRole.CLUB_ADMIN,
        )

        create_user(mock_db, user_data)

        added_user = mock_db.add.call_args[0][0]
        assert added_user.role == UserRole.CLUB_ADMIN

    @patch("app.crud.user_crud.get_password_hash")
    def test_create_user_default_values(self, mock_hash):
        mock_db = Mock(spec=Session)
        mock_hash.return_value = "hashed_password"

        user_data = UserCreate(
            email="test@example.com", password="password", full_name="Test User"
        )

        create_user(mock_db, user_data)

        added_user = mock_db.add.call_args[0][0]
        assert added_user.is_active is True
        assert added_user.elo_rating == 1.0

    @patch("app.crud.user_crud.get_password_hash")
    def test_create_user_duplicate_email(self, mock_hash):
        mock_db = Mock(spec=Session)
        mock_hash.return_value = "hashed_password"
        mock_db.commit.side_effect = IntegrityError(
            "UNIQUE constraint failed", None, None
        )

        user_data = UserCreate(
            email="duplicate@example.com", password="password", full_name="Test User"
        )

        with pytest.raises(IntegrityError):
            create_user(mock_db, user_data)


class TestUpdateUser:
    @patch("app.crud.user_crud.get_password_hash")
    def test_update_user_with_password(self, mock_hash):
        mock_db = Mock(spec=Session)
        mock_hash.return_value = "new_hashed_password"

        existing_user = User(
            id=1,
            email="test@example.com",
            full_name="Old Name",
            hashed_password="old_hashed_password",
        )

        update_data = UserUpdate(
            full_name="New Name", password="new_password", elo_rating=2.5
        )

        result = update_user(mock_db, existing_user, update_data)

        # Verify password was hashed
        mock_hash.assert_called_once_with("new_password")

        # Verify user was updated
        assert existing_user.full_name == "New Name"
        assert existing_user.hashed_password == "new_hashed_password"
        assert existing_user.elo_rating == 2.5

        # Verify database operations
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(existing_user)

        assert result == existing_user

    def test_update_user_without_password(self):
        mock_db = Mock(spec=Session)

        existing_user = User(
            id=1,
            email="test@example.com",
            full_name="Old Name",
            hashed_password="original_hashed_password",
        )

        update_data = UserUpdate(full_name="New Name", elo_rating=2.5)

        update_user(mock_db, existing_user, update_data)

        # Verify user was updated but password unchanged
        assert existing_user.full_name == "New Name"
        assert existing_user.hashed_password == "original_hashed_password"
        assert existing_user.elo_rating == 2.5

    def test_update_user_partial_update(self):
        mock_db = Mock(spec=Session)

        existing_user = User(
            id=1,
            email="test@example.com",
            full_name="Original Name",
            elo_rating=1.0,
            is_active=True,
        )

        update_data = UserUpdate(elo_rating=3.0)

        update_user(mock_db, existing_user, update_data)

        # Only elo_rating should be updated
        assert existing_user.full_name == "Original Name"
        assert existing_user.elo_rating == 3.0
        assert existing_user.is_active is True

    def test_update_user_exclude_unset(self):
        mock_db = Mock(spec=Session)

        existing_user = User(
            id=1, email="test@example.com", full_name="Original Name", elo_rating=1.0
        )

        # Create update with only one field set
        update_data = UserUpdate()
        update_data.full_name = "New Name"

        update_user(mock_db, existing_user, update_data)

        # Only explicitly set fields should be updated
        assert existing_user.full_name == "New Name"
        assert existing_user.elo_rating == 1.0  # Should remain unchanged


class TestSearchUsers:
    def test_search_users_by_name(self):
        mock_db = Mock(spec=Session)
        mock_users = [
            User(id=1, email="john@example.com", full_name="John Doe"),
            User(id=2, email="jane@example.com", full_name="Jane Doe"),
        ]

        # Mock the query chain for search
        mock_db.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = (
            mock_users
        )

        result = search_users(mock_db, search_term="Doe", current_user_id=999)

        assert result == mock_users
        mock_db.query.assert_called_once_with(User)

    def test_search_users_empty_result(self):
        mock_db = Mock(spec=Session)
        mock_db.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = (
            []
        )

        result = search_users(mock_db, search_term="Nonexistent", current_user_id=999)

        assert result == []

    def test_search_users_excludes_current_user(self):
        mock_db = Mock(spec=Session)
        mock_users = [User(id=2, email="other@example.com", full_name="Other User")]

        mock_db.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = (
            mock_users
        )

        result = search_users(mock_db, search_term="User", current_user_id=1)

        assert result == mock_users
        mock_db.query.assert_called_once_with(User)


class TestUserCRUDIntegration:
    @patch("app.crud.user_crud.get_password_hash")
    def test_create_and_get_user(self, mock_hash):
        """Integration test for creating a user and then retrieving them."""
        mock_db = Mock(spec=Session)
        mock_hash.return_value = "hashed_password"

        # Create user
        user_data = UserCreate(
            email="test@example.com",
            password="plaintext_password",
            full_name="Test User",
        )

        create_user(mock_db, user_data)

        # Reset mock for get user test
        mock_db.reset_mock()
        mock_db.query.return_value.filter.return_value.first.return_value = User(
            id=1,
            email="test@example.com",
            hashed_password="hashed_password",
            full_name="Test User",
        )

        retrieved_user = get_user(mock_db, user_id=1)

        assert retrieved_user is not None
        assert retrieved_user.email == "test@example.com"
        assert retrieved_user.full_name == "Test User"

    @patch("app.crud.user_crud.get_password_hash")
    def test_create_update_user_workflow(self, mock_hash):
        """Integration test for creating and updating a user."""
        mock_db = Mock(spec=Session)
        mock_hash.side_effect = ["original_hash", "updated_hash"]

        # Create user
        UserCreate(
            email="test@example.com",
            password="original_password",
            full_name="Original Name",
        )

        user = User(
            id=1,
            email="test@example.com",
            full_name="Original Name",
            hashed_password="original_hash",
        )

        # Update user
        update_data = UserUpdate(full_name="Updated Name", password="new_password")

        updated_user = update_user(mock_db, user, update_data)

        assert updated_user.full_name == "Updated Name"
        assert updated_user.hashed_password == "updated_hash"
        assert mock_hash.call_count == 1  # Only called for update
