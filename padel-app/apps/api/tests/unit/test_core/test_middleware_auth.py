from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.middleware.auth import AuthenticationMiddleware
from app.models.user import User
from app.models.user_role import UserRole
from app.schemas.token_schemas import TokenData


class TestAuthenticationMiddleware:
    """Test suite for AuthenticationMiddleware."""

    @pytest.fixture
    def middleware(self):
        """Create an AuthenticationMiddleware instance."""
        return AuthenticationMiddleware(app=MagicMock())

    @pytest.fixture
    def mock_request(self):
        """Create a mock request object."""
        request = MagicMock(spec=Request)
        request.state = MagicMock()
        request.headers = {}
        return request

    @pytest.fixture
    def mock_user(self):
        """Create a mock user for testing."""
        user = MagicMock(spec=User)
        user.id = 1
        user.email = "test@example.com"
        user.is_active = True
        user.role = UserRole.PLAYER
        return user

    @pytest.fixture
    def mock_token_data(self):
        """Create mock token data."""
        return TokenData(
            sub="test@example.com", role=UserRole.PLAYER, token_type="access"
        )

    @pytest.mark.asyncio
    async def test_middleware_inherits_from_base_http_middleware(self, middleware):
        """Test that AuthenticationMiddleware inherits from BaseHTTPMiddleware."""
        assert isinstance(middleware, BaseHTTPMiddleware)

    @pytest.mark.asyncio
    async def test_dispatch_without_auth_header(self, middleware, mock_request):
        """Test dispatch method without authorization header."""
        # Mock call_next
        call_next = AsyncMock()
        expected_response = MagicMock()
        call_next.return_value = expected_response

        # Call dispatch
        response = await middleware.dispatch(mock_request, call_next)

        # Verify user is set to None
        assert mock_request.state.user is None

        # Verify call_next was called
        call_next.assert_called_once_with(mock_request)

        # Verify response is returned
        assert response == expected_response

    @pytest.mark.asyncio
    async def test_dispatch_with_valid_bearer_token(
        self, middleware, mock_request, mock_user, mock_token_data
    ):
        """Test dispatch method with valid bearer token."""
        # Set up authorization header
        mock_request.headers = {"Authorization": "Bearer valid_token"}

        # Mock call_next
        call_next = AsyncMock()
        expected_response = MagicMock()
        call_next.return_value = expected_response

        # Mock dependencies
        with patch(
            "app.middleware.auth.decode_token_payload", return_value=mock_token_data
        ), patch(
            "app.middleware.auth.user_crud.get_user_by_email",
            return_value=mock_user,
        ), patch(
            "app.middleware.auth.SessionLocal"
        ) as mock_session_local:
            mock_db = MagicMock()
            mock_session_local.return_value = mock_db

            # Call dispatch
            response = await middleware.dispatch(mock_request, call_next)

            # Verify user is set
            assert mock_request.state.user == mock_user

            # Verify database session was closed
            mock_db.close.assert_called_once()

            # Verify call_next was called
            call_next.assert_called_once_with(mock_request)

            # Verify response is returned
            assert response == expected_response

    @pytest.mark.asyncio
    async def test_dispatch_with_invalid_bearer_token(self, middleware, mock_request):
        """Test dispatch method with invalid bearer token."""
        # Set up authorization header
        mock_request.headers = {"Authorization": "Bearer invalid_token"}

        # Mock call_next
        call_next = AsyncMock()
        expected_response = MagicMock()
        call_next.return_value = expected_response

        # Mock decode_token_payload to raise an exception
        with patch(
            "app.middleware.auth.decode_token_payload",
            side_effect=Exception("Invalid token"),
        ), patch("app.middleware.auth.SessionLocal") as mock_session_local:
            mock_db = MagicMock()
            mock_session_local.return_value = mock_db

            # Call dispatch
            response = await middleware.dispatch(mock_request, call_next)

            # Verify user is set to None (middleware doesn't block)
            assert mock_request.state.user is None

            # Verify database session was closed
            mock_db.close.assert_called_once()

            # Verify call_next was called
            call_next.assert_called_once_with(mock_request)

            # Verify response is returned
            assert response == expected_response

    @pytest.mark.asyncio
    async def test_dispatch_with_malformed_auth_header(self, middleware, mock_request):
        """Test dispatch method with malformed authorization header."""
        # Set up malformed authorization header
        mock_request.headers = {"Authorization": "InvalidFormat"}

        # Mock call_next
        call_next = AsyncMock()
        expected_response = MagicMock()
        call_next.return_value = expected_response

        # Call dispatch
        response = await middleware.dispatch(mock_request, call_next)

        # Verify user is set to None
        assert mock_request.state.user is None

        # Verify call_next was called
        call_next.assert_called_once_with(mock_request)

        # Verify response is returned
        assert response == expected_response

    @pytest.mark.asyncio
    async def test_dispatch_with_non_bearer_token(self, middleware, mock_request):
        """Test dispatch method with non-bearer authorization scheme."""
        # Set up non-bearer authorization header
        mock_request.headers = {"Authorization": "Basic dXNlcjpwYXNz"}

        # Mock call_next
        call_next = AsyncMock()
        expected_response = MagicMock()
        call_next.return_value = expected_response

        # Call dispatch
        response = await middleware.dispatch(mock_request, call_next)

        # Verify user is set to None
        assert mock_request.state.user is None

        # Verify call_next was called
        call_next.assert_called_once_with(mock_request)

        # Verify response is returned
        assert response == expected_response

    @pytest.mark.asyncio
    async def test_dispatch_with_user_not_found(
        self, middleware, mock_request, mock_token_data
    ):
        """Test dispatch method when user is not found in database."""
        # Set up authorization header
        mock_request.headers = {"Authorization": "Bearer valid_token"}

        # Mock call_next
        call_next = AsyncMock()
        expected_response = MagicMock()
        call_next.return_value = expected_response

        # Mock dependencies
        with patch(
            "app.middleware.auth.decode_token_payload", return_value=mock_token_data
        ), patch(
            "app.middleware.auth.user_crud.get_user_by_email", return_value=None
        ), patch(
            "app.middleware.auth.SessionLocal"
        ) as mock_session_local:
            mock_db = MagicMock()
            mock_session_local.return_value = mock_db

            # Call dispatch
            response = await middleware.dispatch(mock_request, call_next)

            # Verify user is set to None
            assert mock_request.state.user is None

            # Verify database session was closed
            mock_db.close.assert_called_once()

            # Verify call_next was called
            call_next.assert_called_once_with(mock_request)

            # Verify response is returned
            assert response == expected_response

    @pytest.mark.asyncio
    async def test_dispatch_with_token_missing_subject(self, middleware, mock_request):
        """Test dispatch method with token missing subject."""
        # Set up authorization header
        mock_request.headers = {"Authorization": "Bearer valid_token"}

        # Mock call_next
        call_next = AsyncMock()
        expected_response = MagicMock()
        call_next.return_value = expected_response

        # Mock token data without subject
        mock_token_data = TokenData(sub=None, role=UserRole.PLAYER, token_type="access")

        # Mock dependencies
        with patch(
            "app.middleware.auth.decode_token_payload", return_value=mock_token_data
        ), patch("app.middleware.auth.SessionLocal") as mock_session_local:
            mock_db = MagicMock()
            mock_session_local.return_value = mock_db

            # Call dispatch
            response = await middleware.dispatch(mock_request, call_next)

            # Verify user is set to None
            assert mock_request.state.user is None

            # Verify database session was closed
            mock_db.close.assert_called_once()

            # Verify call_next was called
            call_next.assert_called_once_with(mock_request)

            # Verify response is returned
            assert response == expected_response

    @pytest.mark.asyncio
    async def test_dispatch_handles_database_exception(
        self, middleware, mock_request, mock_token_data
    ):
        """Test dispatch method handles database exceptions gracefully."""
        # Set up authorization header
        mock_request.headers = {"Authorization": "Bearer valid_token"}

        # Mock call_next
        call_next = AsyncMock()
        expected_response = MagicMock()
        call_next.return_value = expected_response

        # Mock dependencies
        with patch(
            "app.middleware.auth.decode_token_payload", return_value=mock_token_data
        ), patch(
            "app.middleware.auth.user_crud.get_user_by_email",
            side_effect=Exception("Database error"),
        ), patch(
            "app.middleware.auth.SessionLocal"
        ) as mock_session_local:
            mock_db = MagicMock()
            mock_session_local.return_value = mock_db

            # Call dispatch
            response = await middleware.dispatch(mock_request, call_next)

            # Verify user is set to None (middleware doesn't block)
            assert mock_request.state.user is None

            # Verify database session was closed
            mock_db.close.assert_called_once()

            # Verify call_next was called
            call_next.assert_called_once_with(mock_request)

            # Verify response is returned
            assert response == expected_response

    @pytest.mark.asyncio
    async def test_dispatch_case_insensitive_bearer_scheme(
        self, middleware, mock_request, mock_user, mock_token_data
    ):
        """Test dispatch method with case-insensitive bearer scheme."""
        # Set up authorization header with different case
        mock_request.headers = {"Authorization": "BEARER valid_token"}

        # Mock call_next
        call_next = AsyncMock()
        expected_response = MagicMock()
        call_next.return_value = expected_response

        # Mock dependencies
        with patch(
            "app.middleware.auth.decode_token_payload", return_value=mock_token_data
        ), patch(
            "app.middleware.auth.user_crud.get_user_by_email",
            return_value=mock_user,
        ), patch(
            "app.middleware.auth.SessionLocal"
        ) as mock_session_local:
            mock_db = MagicMock()
            mock_session_local.return_value = mock_db

            # Call dispatch
            response = await middleware.dispatch(mock_request, call_next)

            # Verify user is set
            assert mock_request.state.user == mock_user

            # Verify database session was closed
            mock_db.close.assert_called_once()

            # Verify call_next was called
            call_next.assert_called_once_with(mock_request)

            # Verify response is returned
            assert response == expected_response

    @pytest.mark.asyncio
    async def test_dispatch_with_multiple_spaces_in_auth_header(
        self, middleware, mock_request
    ):
        """Test dispatch method with multiple spaces in authorization header."""
        # Set up authorization header with multiple spaces
        mock_request.headers = {"Authorization": "Bearer  token  with  spaces"}

        # Mock call_next
        call_next = AsyncMock()
        expected_response = MagicMock()
        call_next.return_value = expected_response

        # Call dispatch (should handle gracefully)
        response = await middleware.dispatch(mock_request, call_next)

        # Verify user is set to None
        assert mock_request.state.user is None

        # Verify call_next was called
        call_next.assert_called_once_with(mock_request)

        # Verify response is returned
        assert response == expected_response

    @pytest.mark.asyncio
    async def test_dispatch_initializes_user_state(self, middleware, mock_request):
        """Test that dispatch always initializes request.state.user."""
        # Mock call_next
        call_next = AsyncMock()
        expected_response = MagicMock()
        call_next.return_value = expected_response

        # Call dispatch without any auth header
        response = await middleware.dispatch(mock_request, call_next)

        # Verify user state is initialized to None
        assert hasattr(mock_request.state, "user")
        assert mock_request.state.user is None

        # Verify call_next was called
        call_next.assert_called_once_with(mock_request)

        # Verify response is returned
        assert response == expected_response

    @pytest.mark.asyncio
    async def test_dispatch_preserves_existing_response(self, middleware, mock_request):
        """Test that dispatch preserves the response from call_next."""
        # Mock call_next to return a specific response
        call_next = AsyncMock()
        expected_response = JSONResponse(content={"message": "test"}, status_code=200)
        call_next.return_value = expected_response

        # Call dispatch
        response = await middleware.dispatch(mock_request, call_next)

        # Verify the exact response is returned
        assert response is expected_response

    @pytest.mark.asyncio
    async def test_dispatch_with_empty_authorization_header(
        self, middleware, mock_request
    ):
        """Test dispatch method with empty authorization header."""
        # Set up empty authorization header
        mock_request.headers = {"Authorization": ""}

        # Mock call_next
        call_next = AsyncMock()
        expected_response = MagicMock()
        call_next.return_value = expected_response

        # Call dispatch
        response = await middleware.dispatch(mock_request, call_next)

        # Verify user is set to None
        assert mock_request.state.user is None

        # Verify call_next was called
        call_next.assert_called_once_with(mock_request)

        # Verify response is returned
        assert response == expected_response

    @pytest.mark.asyncio
    async def test_dispatch_database_session_cleanup(
        self, middleware, mock_request, mock_token_data
    ):
        """Test that database session is always cleaned up."""
        # Set up authorization header
        mock_request.headers = {"Authorization": "Bearer valid_token"}

        # Mock call_next
        call_next = AsyncMock()
        expected_response = MagicMock()
        call_next.return_value = expected_response

        # Mock dependencies
        with patch(
            "app.middleware.auth.decode_token_payload", return_value=mock_token_data
        ), patch(
            "app.middleware.auth.user_crud.get_user_by_email",
            side_effect=Exception("Database error"),
        ), patch(
            "app.middleware.auth.SessionLocal"
        ) as mock_session_local:
            mock_db = MagicMock()
            mock_session_local.return_value = mock_db

            # Call dispatch
            await middleware.dispatch(mock_request, call_next)

            # Verify database session was closed even with exception
            mock_db.close.assert_called_once()


class TestMiddlewareIntegration:
    """Test suite for middleware integration with the application."""

    def test_middleware_can_be_imported(self):
        """Test that middleware can be imported without errors."""
        from app.middleware.auth import AuthenticationMiddleware

        assert AuthenticationMiddleware is not None

    def test_middleware_dependencies_available(self):
        """Test that all middleware dependencies are available."""
        from app.middleware.auth import SessionLocal, decode_token_payload, user_crud

        assert decode_token_payload is not None
        assert user_crud is not None
        assert SessionLocal is not None

    def test_middleware_error_handling_philosophy(self):
        """Test that middleware follows the correct error handling philosophy."""
        # The middleware should NOT block requests when authentication fails
        # It should only attach user information when available
        # This test documents the expected behavior
        middleware = AuthenticationMiddleware(app=MagicMock())

        # This is a philosophical test to ensure the middleware doesn't block
        # The actual behavior is tested in other test methods
        assert hasattr(middleware, "dispatch")
        assert callable(middleware.dispatch)

    @pytest.mark.asyncio
    async def test_middleware_with_different_user_roles(self):
        """Test middleware with different user roles."""
        middleware = AuthenticationMiddleware(app=MagicMock())

        for role in UserRole:
            mock_request = MagicMock(spec=Request)
            mock_request.state = MagicMock()
            mock_request.headers = {"Authorization": "Bearer valid_token"}

            mock_user = MagicMock(spec=User)
            mock_user.role = role

            mock_token_data = TokenData(
                sub="test@example.com", role=role, token_type="access"
            )

            # Mock call_next
            call_next = AsyncMock()
            expected_response = MagicMock()
            call_next.return_value = expected_response

            # Mock dependencies
            with patch(
                "app.middleware.auth.decode_token_payload", return_value=mock_token_data
            ), patch(
                "app.middleware.auth.user_crud.get_user_by_email",
                return_value=mock_user,
            ), patch(
                "app.middleware.auth.SessionLocal"
            ) as mock_session_local:
                mock_db = MagicMock()
                mock_session_local.return_value = mock_db

                # Call dispatch
                await middleware.dispatch(mock_request, call_next)

                # Verify user is set with correct role
                assert mock_request.state.user == mock_user
                assert mock_request.state.user.role == role
