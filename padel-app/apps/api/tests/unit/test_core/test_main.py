import pytest
import os
from unittest.mock import patch, MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.main import app
from app.core.config import settings
from app.middleware.auth import AuthenticationMiddleware


class TestFastAPIApp:
    """Test suite for FastAPI application configuration."""
    
    def test_app_is_fastapi_instance(self):
        """Test that app is a FastAPI instance."""
        assert isinstance(app, FastAPI)
    
    def test_app_title_from_settings(self):
        """Test that app title is set from settings."""
        assert app.title == settings.PROJECT_NAME
    
    def test_app_version(self):
        """Test that app version is set correctly."""
        assert app.version == "0.1.0"
    
    def test_app_description(self):
        """Test that app description is set correctly."""
        expected_description = "API for the PadelGo application to manage bookings, players, and games."
        assert app.description == expected_description
    
    def test_app_openapi_url(self):
        """Test that OpenAPI URL is set correctly."""
        expected_url = f"{settings.API_V1_STR}/openapi.json"
        assert app.openapi_url == expected_url


class TestMiddleware:
    """Test suite for application middleware configuration."""
    
    def test_cors_middleware_is_added(self):
        """Test that CORS middleware is added to the app."""
        # Check if CORSMiddleware is in the middleware stack
        middleware_types = [type(middleware.cls) for middleware in app.user_middleware]
        assert CORSMiddleware in middleware_types
    
    def test_authentication_middleware_is_added(self):
        """Test that Authentication middleware is added to the app."""
        # Check if AuthenticationMiddleware is in the middleware stack
        middleware_types = [type(middleware.cls) for middleware in app.user_middleware]
        assert AuthenticationMiddleware in middleware_types
    
    def test_cors_middleware_configuration(self):
        """Test CORS middleware configuration."""
        # Find the CORS middleware in the stack
        cors_middleware = None
        for middleware in app.user_middleware:
            if middleware.cls == CORSMiddleware:
                cors_middleware = middleware
                break
        
        assert cors_middleware is not None
        
        # Check CORS configuration
        cors_kwargs = cors_middleware.kwargs
        assert cors_kwargs.get('allow_origins') == ["*"]
        assert cors_kwargs.get('allow_credentials') is False
        assert "GET" in cors_kwargs.get('allow_methods', [])
        assert "POST" in cors_kwargs.get('allow_methods', [])
        assert "PUT" in cors_kwargs.get('allow_methods', [])
        assert "DELETE" in cors_kwargs.get('allow_methods', [])
        assert "PATCH" in cors_kwargs.get('allow_methods', [])
        assert "OPTIONS" in cors_kwargs.get('allow_methods', [])
        assert cors_kwargs.get('allow_headers') == ["*"]
    
    def test_middleware_order(self):
        """Test that middleware is added in the correct order."""
        # CORS middleware should be added first, then Authentication middleware
        middleware_classes = [middleware.cls for middleware in app.user_middleware]
        
        # Find the indices of both middleware types
        cors_index = next((i for i, cls in enumerate(middleware_classes) if cls == CORSMiddleware), -1)
        auth_index = next((i for i, cls in enumerate(middleware_classes) if cls == AuthenticationMiddleware), -1)
        
        assert cors_index != -1, "CORS middleware not found"
        assert auth_index != -1, "Authentication middleware not found"
        
        # CORS should come before Authentication (lower index means added first)
        assert cors_index < auth_index


class TestStaticFiles:
    """Test suite for static files configuration."""
    
    def test_static_files_mount(self):
        """Test that static files are mounted correctly."""
        # Check if static files are mounted at /static
        static_mount = None
        for route in app.routes:
            if hasattr(route, 'path') and route.path == "/static":
                static_mount = route
                break
        
        assert static_mount is not None
        assert static_mount.name == "static"
    
    def test_static_files_directory_path(self):
        """Test that static files directory path is correct."""
        from app.main import static_files_path
        expected_path = Path(__file__).parent.parent.parent.parent / "app" / "static"
        
        # Convert to absolute paths for comparison
        assert static_files_path.resolve() == expected_path.resolve()


class TestRouters:
    """Test suite for router configuration."""
    
    def test_auth_router_included(self):
        """Test that auth router is included with correct prefix."""
        auth_routes = [route for route in app.routes if hasattr(route, 'path') and route.path.startswith(f"{settings.API_V1_STR}/auth")]
        assert len(auth_routes) > 0
    
    def test_clubs_router_included(self):
        """Test that clubs router is included with correct prefix."""
        clubs_routes = [route for route in app.routes if hasattr(route, 'path') and route.path.startswith(f"{settings.API_V1_STR}/clubs")]
        assert len(clubs_routes) > 0
    
    def test_courts_router_included(self):
        """Test that courts router is included with correct prefix."""
        courts_routes = [route for route in app.routes if hasattr(route, 'path') and route.path.startswith(f"{settings.API_V1_STR}/courts")]
        assert len(courts_routes) > 0
    
    def test_bookings_router_included(self):
        """Test that bookings router is included with correct prefix."""
        bookings_routes = [route for route in app.routes if hasattr(route, 'path') and route.path.startswith(f"{settings.API_V1_STR}/bookings")]
        assert len(bookings_routes) > 0
    
    def test_games_router_included(self):
        """Test that games router is included with correct prefix."""
        games_routes = [route for route in app.routes if hasattr(route, 'path') and route.path.startswith(f"{settings.API_V1_STR}/games")]
        assert len(games_routes) > 0
    
    def test_users_router_included(self):
        """Test that users router is included with correct prefix."""
        users_routes = [route for route in app.routes if hasattr(route, 'path') and route.path.startswith(f"{settings.API_V1_STR}/users")]
        assert len(users_routes) > 0
    
    def test_admin_router_included(self):
        """Test that admin router is included with correct prefix."""
        admin_routes = [route for route in app.routes if hasattr(route, 'path') and route.path.startswith(f"{settings.API_V1_STR}/admin")]
        assert len(admin_routes) > 0
    
    def test_leaderboard_router_included(self):
        """Test that leaderboard router is included with correct prefix."""
        leaderboard_routes = [route for route in app.routes if hasattr(route, 'path') and route.path.startswith(f"{settings.API_V1_STR}/leaderboard")]
        assert len(leaderboard_routes) > 0
    
    def test_public_router_included(self):
        """Test that public router is included with correct prefix."""
        public_routes = [route for route in app.routes if hasattr(route, 'path') and route.path.startswith(f"{settings.API_V1_STR}/public")]
        assert len(public_routes) > 0
    
    def test_tournaments_router_included(self):
        """Test that tournaments router is included with correct prefix."""
        tournaments_routes = [route for route in app.routes if hasattr(route, 'path') and route.path.startswith(f"{settings.API_V1_STR}") and "tournament" in route.path.lower()]
        assert len(tournaments_routes) > 0


class TestExceptionHandlers:
    """Test suite for custom exception handlers."""
    
    def test_validation_exception_handler_registered(self):
        """Test that validation exception handler is registered."""
        from fastapi.exceptions import RequestValidationError
        
        # Check if the exception handler is registered
        assert RequestValidationError in app.exception_handlers
    
    def test_validation_exception_handler_function(self):
        """Test the validation exception handler function."""
        from app.main import validation_exception_handler
        from fastapi.exceptions import RequestValidationError
        from fastapi import Request
        
        # Create a mock request and exception
        mock_request = MagicMock(spec=Request)
        mock_exc = MagicMock(spec=RequestValidationError)
        mock_exc.errors.return_value = [{"msg": "test error"}]
        mock_exc.body = b'{"test": "data"}'
        
        # Test the handler
        import asyncio
        response = asyncio.run(validation_exception_handler(mock_request, mock_exc))
        
        assert response.status_code == 422
        assert "detail" in response.body.decode()
        assert "body" in response.body.decode()


class TestStartupEvents:
    """Test suite for application startup events."""
    
    def test_startup_event_registered(self):
        """Test that startup event is registered."""
        # Check if startup event handlers are registered
        assert len(app.router.on_startup) > 0
    
    @patch('cloudinary.config')
    def test_startup_event_configures_cloudinary(self, mock_cloudinary_config):
        """Test that startup event configures Cloudinary."""
        # Trigger the startup event
        import asyncio
        
        # Get the startup event handler
        startup_handler = app.router.on_startup[0]
        
        # Run the startup event
        asyncio.run(startup_handler())
        
        # Verify that cloudinary.config was called with correct parameters
        mock_cloudinary_config.assert_called_once_with(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True,
        )


class TestRootEndpoints:
    """Test suite for root endpoints."""
    
    def test_root_endpoint_exists(self):
        """Test that root endpoint exists."""
        root_routes = [route for route in app.routes if hasattr(route, 'path') and route.path == "/"]
        assert len(root_routes) > 0
    
    def test_health_endpoint_exists(self):
        """Test that health endpoint exists."""
        health_routes = [route for route in app.routes if hasattr(route, 'path') and route.path == "/health"]
        assert len(health_routes) > 0
    
    def test_root_endpoint_response(self):
        """Test root endpoint response."""
        client = TestClient(app)
        response = client.get("/")
        
        assert response.status_code == 200
        assert response.json() == {"message": f"Welcome to {settings.PROJECT_NAME}"}
    
    def test_health_endpoint_response(self):
        """Test health endpoint response."""
        client = TestClient(app)
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestApplicationIntegration:
    """Test suite for application integration and configuration."""
    
    def test_app_can_be_imported(self):
        """Test that the app can be imported without errors."""
        from app.main import app
        assert app is not None
    
    def test_app_openapi_schema(self):
        """Test that OpenAPI schema is generated correctly."""
        schema = app.openapi()
        
        assert "openapi" in schema
        assert schema["info"]["title"] == settings.PROJECT_NAME
        assert schema["info"]["version"] == "0.1.0"
    
    def test_app_routes_accessible(self):
        """Test that app routes are accessible."""
        client = TestClient(app)
        
        # Test that we can access the OpenAPI schema
        response = client.get(f"{settings.API_V1_STR}/openapi.json")
        assert response.status_code == 200
        
        # Test that we can access the docs
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_app_cors_functionality(self):
        """Test that CORS functionality works."""
        client = TestClient(app)
        
        # Test preflight request
        response = client.options("/", headers={"Origin": "http://localhost:3000"})
        assert response.status_code == 200
        
        # Check CORS headers
        assert "access-control-allow-origin" in response.headers
    
    def test_app_authentication_middleware_functionality(self):
        """Test that authentication middleware is working."""
        client = TestClient(app)
        
        # Test without authentication
        response = client.get("/")
        assert response.status_code == 200
        
        # Test with invalid token
        response = client.get("/", headers={"Authorization": "Bearer invalid_token"})
        assert response.status_code == 200  # Should still work as middleware doesn't block
    
    def test_app_static_files_functionality(self):
        """Test that static files are served correctly."""
        client = TestClient(app)
        
        # Test static file access (this will 404 if no file exists, but should not error)
        response = client.get("/static/test.txt")
        # Should return 404 for non-existent file, not 500
        assert response.status_code == 404
    
    def test_app_validation_error_handling(self):
        """Test that validation errors are handled correctly."""
        client = TestClient(app)
        
        # Test with invalid JSON to trigger validation error
        response = client.post(
            f"{settings.API_V1_STR}/auth/login",
            json={"invalid": "data"},
            headers={"Content-Type": "application/json"}
        )
        
        # Should return 422 for validation error
        assert response.status_code == 422
        
        # Response should contain error details
        response_data = response.json()
        assert "detail" in response_data
        assert "body" in response_data
    
    def test_app_settings_integration(self):
        """Test that app integrates correctly with settings."""
        # Test that all settings-dependent configurations are correct
        assert app.title == settings.PROJECT_NAME
        assert app.openapi_url == f"{settings.API_V1_STR}/openapi.json"
        
        # Test that routers use correct API version
        api_routes = [route for route in app.routes if hasattr(route, 'path') and route.path.startswith(settings.API_V1_STR)]
        assert len(api_routes) > 0
    
    def test_app_dependency_injection(self):
        """Test that dependency injection is working correctly."""
        from app.database import get_db
        from app.core.security import get_current_user
        
        # Test that dependencies are properly configured
        # This is more of a smoke test to ensure imports work
        assert callable(get_db)
        assert callable(get_current_user)