from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import (
    booking_admin_checker,
    club_admin_checker,
    role_checker,
)
from app.models.booking import Booking
from app.models.club_admin import ClubAdmin
from app.models.court import Court
from app.models.user import User
from app.models.user_role import UserRole


class TestRoleChecker:
    """Test suite for RoleChecker dependency."""

    @pytest.fixture
    def mock_user(self):
        """Create a mock user for testing."""
        user = MagicMock(spec=User)
        user.id = 1
        user.email = "test@example.com"
        user.is_active = True
        return user

    def test_role_checker_with_allowed_single_role(self, mock_user):
        """Test role_checker with a single allowed role that matches user role."""
        mock_user.role = UserRole.ADMIN
        check_role = role_checker([UserRole.ADMIN])

        # Should not raise an exception
        result = check_role(mock_user)
        assert result == mock_user

    def test_role_checker_with_allowed_multiple_roles(self, mock_user):
        """Test RoleChecker with multiple allowed roles where user has one of them."""
        mock_user.role = UserRole.PLAYER
        check_role = role_checker(
            [UserRole.ADMIN, UserRole.PLAYER, UserRole.CLUB_ADMIN]
        )

        # Should not raise an exception
        result = check_role(mock_user)
        assert result == mock_user

    def test_role_checker_with_forbidden_role(self, mock_user):
        """Test RoleChecker with a role that is not allowed."""
        mock_user.role = UserRole.PLAYER
        check_role = role_checker([UserRole.ADMIN, UserRole.SUPER_ADMIN])

        with pytest.raises(HTTPException) as excinfo:
            check_role(mock_user)

        assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN
        assert "is not permitted to access this resource" in excinfo.value.detail
        assert "PLAYER" in excinfo.value.detail

    def test_role_checker_with_super_admin_role(self, mock_user):
        """Test RoleChecker with super admin role."""
        mock_user.role = UserRole.SUPER_ADMIN
        check_role = role_checker([UserRole.SUPER_ADMIN])

        result = check_role(mock_user)
        assert result == mock_user

    def test_role_checker_with_club_admin_role(self, mock_user):
        """Test RoleChecker with club admin role."""
        mock_user.role = UserRole.CLUB_ADMIN
        check_role = role_checker([UserRole.CLUB_ADMIN, UserRole.ADMIN])

        result = check_role(mock_user)
        assert result == mock_user

    def test_role_checker_with_empty_allowed_roles(self, mock_user):
        """Test RoleChecker with empty allowed roles list."""
        mock_user.role = UserRole.PLAYER
        check_role = role_checker([])

        with pytest.raises(HTTPException) as excinfo:
            check_role(mock_user)

        assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN

    def test_role_checker_returns_callable(self):
        """Test that RoleChecker returns a callable function."""
        role_checker([UserRole.ADMIN])
        check_function = role_checker._check_role

        assert callable(check_function)

    def test_role_checker_with_all_roles(self, mock_user):
        """Test RoleChecker with all possible roles."""
        all_roles = [
            UserRole.PLAYER,
            UserRole.ADMIN,
            UserRole.SUPER_ADMIN,
            UserRole.CLUB_ADMIN,
        ]

        for role in all_roles:
            mock_user.role = role
            check_role = role_checker(all_roles)

            result = check_role(mock_user)
            assert result == mock_user


class TestClubAdminChecker:
    """Test suite for ClubAdminChecker dependency."""

    @pytest.fixture
    def mock_user(self):
        """Create a mock user for testing."""
        user = MagicMock(spec=User)
        user.id = 1
        user.email = "test@example.com"
        user.is_active = True
        return user

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return MagicMock(spec=Session)

    @pytest.fixture
    def mock_club_admin(self):
        """Create a mock club admin record."""
        club_admin = MagicMock(spec=ClubAdmin)
        club_admin.user_id = 1
        club_admin.club_id = 1
        return club_admin

    def test_club_admin_checker_with_super_admin(self, mock_user, mock_db):
        """Test ClubAdminChecker with super admin user."""
        mock_user.role = UserRole.SUPER_ADMIN
        check_club_admin = club_admin_checker()

        result = check_club_admin(club_id=1, current_user=mock_user, db=mock_db)
        assert result == mock_user

    def test_club_admin_checker_with_club_admin_access(
        self, mock_user, mock_db, mock_club_admin
    ):
        """Test ClubAdminChecker with user who has club admin access."""
        mock_user.role = UserRole.CLUB_ADMIN

        with patch(
            "app.core.dependencies.club_admin_crud.get_club_admin",
            return_value=mock_club_admin,
        ):
            check_club_admin = club_admin_checker()
            result = check_club_admin(club_id=1, current_user=mock_user, db=mock_db)
            assert result == mock_user

    def test_club_admin_checker_without_club_admin_access(self, mock_user, mock_db):
        """Test ClubAdminChecker with user who doesn't have club admin access."""
        mock_user.role = UserRole.PLAYER

        with patch(
            "app.core.dependencies.club_admin_crud.get_club_admin", return_value=None
        ):
            check_club_admin = club_admin_checker()

            with pytest.raises(HTTPException) as excinfo:
                check_club_admin(club_id=1, current_user=mock_user, db=mock_db)

            assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN
            assert "administrative access to this club" in excinfo.value.detail

    def test_club_admin_checker_with_different_club_id(self, mock_user, mock_db):
        """Test ClubAdminChecker with different club IDs."""
        mock_user.role = UserRole.CLUB_ADMIN

        # Mock club admin access for club_id=1 but not for club_id=2
        def mock_get_club_admin(db, user_id, club_id):
            if club_id == 1:
                return MagicMock(spec=ClubAdmin)
            return None

        with patch(
            "app.core.dependencies.club_admin_crud.get_club_admin",
            side_effect=mock_get_club_admin,
        ):
            check_club_admin = club_admin_checker()

            # Should succeed for club_id=1
            result = check_club_admin(club_id=1, current_user=mock_user, db=mock_db)
            assert result == mock_user

            # Should fail for club_id=2
            with pytest.raises(HTTPException) as excinfo:
                check_club_admin(club_id=2, current_user=mock_user, db=mock_db)

            assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN

    def test_club_admin_checker_calls_crud_with_correct_parameters(
        self, mock_user, mock_db
    ):
        """Test that ClubAdminChecker calls club_admin_crud with correct parameters."""
        mock_user.role = UserRole.CLUB_ADMIN
        mock_user.id = 123
        club_id = 456

        with patch(
            "app.core.dependencies.club_admin_crud.get_club_admin", return_value=None
        ) as mock_get_club_admin:
            check_club_admin = club_admin_checker()

            try:
                check_club_admin(club_id=club_id, current_user=mock_user, db=mock_db)
            except HTTPException:
                pass  # Expected to fail

            mock_get_club_admin.assert_called_once_with(
                mock_db, user_id=123, club_id=456
            )

    def test_club_admin_checker_returns_callable(self):
        """Test that ClubAdminChecker returns a callable function."""
        club_admin_checker()
        check_function = club_admin_checker._check_club_admin

        assert callable(check_function)


class TestBookingAdminChecker:
    """Test suite for BookingAdminChecker dependency."""

    @pytest.fixture
    def mock_user(self):
        """Create a mock user for testing."""
        user = MagicMock(spec=User)
        user.id = 1
        user.email = "test@example.com"
        user.is_active = True
        return user

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return MagicMock(spec=Session)

    @pytest.fixture
    def mock_booking(self):
        """Create a mock booking with court and club."""
        booking = MagicMock(spec=Booking)
        booking.id = 1

        court = MagicMock(spec=Court)
        court.club_id = 1
        booking.court = court

        return booking

    @pytest.fixture
    def mock_club_admin(self):
        """Create a mock club admin record."""
        club_admin = MagicMock(spec=ClubAdmin)
        club_admin.user_id = 1
        club_admin.club_id = 1
        return club_admin

    def test_booking_admin_checker_with_super_admin(
        self, mock_user, mock_db, mock_booking
    ):
        """Test BookingAdminChecker with super admin user."""
        mock_user.role = UserRole.SUPER_ADMIN

        with patch(
            "app.core.dependencies.booking_crud.get_booking", return_value=mock_booking
        ):
            booking_admin_checker()
            result = booking_admin_checker(
                booking_id=1, current_user=mock_user, db=mock_db
            )
            assert result == mock_user

    def test_booking_admin_checker_with_club_admin_access(
        self, mock_user, mock_db, mock_booking, mock_club_admin
    ):
        """Test BookingAdminChecker with user who has club admin access."""
        mock_user.role = UserRole.CLUB_ADMIN

        with patch(
            "app.core.dependencies.booking_crud.get_booking", return_value=mock_booking
        ), patch(
            "app.core.dependencies.club_admin_crud.get_club_admin",
            return_value=mock_club_admin,
        ):
            booking_admin_checker()
            result = booking_admin_checker(
                booking_id=1, current_user=mock_user, db=mock_db
            )
            assert result == mock_user

    def test_booking_admin_checker_without_club_admin_access(
        self, mock_user, mock_db, mock_booking
    ):
        """Test BookingAdminChecker with user who doesn't have club admin access."""
        mock_user.role = UserRole.PLAYER

        with patch(
            "app.core.dependencies.booking_crud.get_booking", return_value=mock_booking
        ), patch(
            "app.core.dependencies.club_admin_crud.get_club_admin",
            return_value=None,
        ):
            check_booking_admin = booking_admin_checker()

            with pytest.raises(HTTPException) as excinfo:
                check_booking_admin(booking_id=1, current_user=mock_user, db=mock_db)

            assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN
            assert "administrative access to this club" in excinfo.value.detail

    def test_booking_admin_checker_with_nonexistent_booking(self, mock_user, mock_db):
        """Test BookingAdminChecker with a booking that doesn't exist."""
        mock_user.role = UserRole.ADMIN

        with patch("app.core.dependencies.booking_crud.get_booking", return_value=None):
            booking_admin_checker()

            with pytest.raises(HTTPException) as excinfo:
                booking_admin_checker(
                    booking_id=999, current_user=mock_user, db=mock_db
                )

            assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
            assert "Booking not found" in excinfo.value.detail

    def test_booking_admin_checker_calls_crud_with_correct_parameters(
        self, mock_user, mock_db, mock_booking
    ):
        """Test that BookingAdminChecker calls booking_crud with correct parameters."""
        mock_user.role = UserRole.CLUB_ADMIN
        mock_user.id = 123
        booking_id = 456

        with patch(
            "app.core.dependencies.booking_crud.get_booking", return_value=mock_booking
        ) as mock_get_booking, patch(
            "app.core.dependencies.club_admin_crud.get_club_admin",
            return_value=None,
        ):
            booking_admin_checker()

            try:
                booking_admin_checker(
                    booking_id=booking_id, current_user=mock_user, db=mock_db
                )
            except HTTPException:
                pass  # Expected to fail

            mock_get_booking.assert_called_once_with(mock_db, booking_id=456)

    def test_booking_admin_checker_extracts_club_id_from_booking(
        self, mock_user, mock_db, mock_club_admin
    ):
        """Test that BookingAdminChecker correctly extracts club_id from booking."""
        mock_user.role = UserRole.CLUB_ADMIN
        mock_user.id = 123

        # Create a booking with a specific club_id
        booking = MagicMock(spec=Booking)
        court = MagicMock(spec=Court)
        court.club_id = 789
        booking.court = court

        with patch(
            "app.core.dependencies.booking_crud.get_booking", return_value=booking
        ), patch(
            "app.core.dependencies.club_admin_crud.get_club_admin",
            return_value=mock_club_admin,
        ) as mock_get_club_admin:
            check_booking_admin = booking_admin_checker()
            check_booking_admin(booking_id=1, current_user=mock_user, db=mock_db)

            # Verify that club_admin_crud was called with the correct club_id
            mock_get_club_admin.assert_called_once_with(
                mock_db, user_id=123, club_id=789
            )

    def test_booking_admin_checker_returns_callable(self):
        """Test that BookingAdminChecker returns a callable function."""
        booking_admin_checker()
        check_function = booking_admin_checker._check_booking_admin

        assert callable(check_function)


class TestDependencyIntegration:
    """Test suite for integration between dependency checkers."""

    @pytest.fixture
    def mock_user(self):
        """Create a mock user for testing."""
        user = MagicMock(spec=User)
        user.id = 1
        user.email = "test@example.com"
        user.is_active = True
        return user

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return MagicMock(spec=Session)

    def test_combining_role_checker_and_club_admin_checker(self, mock_user, mock_db):
        """Test combining RoleChecker and ClubAdminChecker."""
        mock_user.role = UserRole.CLUB_ADMIN

        # First check role
        check_role = role_checker([UserRole.CLUB_ADMIN, UserRole.ADMIN])
        role_result = check_role(mock_user)
        assert role_result == mock_user

        # Then check club admin access
        with patch(
            "app.core.dependencies.club_admin_crud.get_club_admin",
            return_value=MagicMock(),
        ):
            club_admin_checker()
            club_result = club_admin_checker(
                club_id=1, current_user=mock_user, db=mock_db
            )
            assert club_result == mock_user

    def test_role_checker_with_all_dependency_roles(self, mock_user):
        """Test RoleChecker with all roles that appear in dependency functions."""
        roles_to_test = [
            UserRole.PLAYER,
            UserRole.ADMIN,
            UserRole.SUPER_ADMIN,
            UserRole.CLUB_ADMIN,
        ]

        for role in roles_to_test:
            mock_user.role = role
            check_role = role_checker([role])
            result = check_role(mock_user)
            assert result == mock_user

    def test_dependency_error_messages_consistency(self, mock_user, mock_db):
        """Test that error messages are consistent across dependency checkers."""
        mock_user.role = UserRole.PLAYER

        # Test RoleChecker error message
        check_role = role_checker([UserRole.ADMIN])
        with pytest.raises(HTTPException) as role_exc:
            check_role(mock_user)

        # Test ClubAdminChecker error message
        with patch(
            "app.core.dependencies.club_admin_crud.get_club_admin", return_value=None
        ):
            check_club_admin = club_admin_checker()
            with pytest.raises(HTTPException) as club_exc:
                check_club_admin(club_id=1, current_user=mock_user, db=mock_db)

        # Test BookingAdminChecker error message
        mock_booking = MagicMock(spec=Booking)
        mock_booking.court = MagicMock(spec=Court)
        mock_booking.court.club_id = 1

        with patch(
            "app.core.dependencies.booking_crud.get_booking", return_value=mock_booking
        ), patch(
            "app.core.dependencies.club_admin_crud.get_club_admin",
            return_value=None,
        ):
            check_booking_admin = booking_admin_checker()
            with pytest.raises(HTTPException) as booking_exc:
                check_booking_admin(booking_id=1, current_user=mock_user, db=mock_db)

        # Check that all dependency errors use 403 status code
        assert role_exc.value.status_code == status.HTTP_403_FORBIDDEN
        assert club_exc.value.status_code == status.HTTP_403_FORBIDDEN
        assert booking_exc.value.status_code == status.HTTP_403_FORBIDDEN

        # Check that club admin errors have consistent messaging
        assert "administrative access to this club" in club_exc.value.detail
        assert "administrative access to this club" in booking_exc.value.detail
