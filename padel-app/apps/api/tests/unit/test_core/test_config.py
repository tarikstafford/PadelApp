import pytest
from unittest.mock import patch, Mock
import os
from pydantic import ValidationError

from app.core.config import Settings


class TestSettingsDefaults:
    def test_settings_default_values(self):
        """Test that settings have correct default values."""
        # Mock required environment variables
        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://test:test@localhost/test',
            'SECRET_KEY': 'test-secret-key',
            'CLOUDINARY_CLOUD_NAME': 'test-cloud',
            'CLOUDINARY_API_KEY': 'test-api-key',
            'CLOUDINARY_API_SECRET': 'test-api-secret'
        }):
            settings = Settings()
            
            assert settings.PROJECT_NAME == "PadelGo API"
            assert settings.API_V1_STR == "/api/v1"
            assert settings.ALGORITHM == "HS256"
            assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 60 * 24 * 1  # 1 day
            assert settings.REFRESH_TOKEN_EXPIRE_MINUTES == 60 * 24 * 30  # 30 days

    def test_settings_cors_origins_default(self):
        """Test CORS origins default values."""
        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://test:test@localhost/test',
            'SECRET_KEY': 'test-secret-key',
            'CLOUDINARY_CLOUD_NAME': 'test-cloud',
            'CLOUDINARY_API_KEY': 'test-api-key',
            'CLOUDINARY_API_SECRET': 'test-api-secret'
        }):
            settings = Settings()
            
            assert len(settings.BACKEND_CORS_ORIGINS) == 2
            assert "http://localhost:3000" in [str(url) for url in settings.BACKEND_CORS_ORIGINS]
            assert "http://localhost:3001" in [str(url) for url in settings.BACKEND_CORS_ORIGINS]


class TestSettingsEnvironmentVariables:
    def test_settings_from_environment(self):
        """Test that settings load correctly from environment variables."""
        test_env = {
            'DATABASE_URL': 'postgresql://user:pass@localhost:5432/mydb',
            'SECRET_KEY': 'my-super-secret-key-123',
            'CLOUDINARY_CLOUD_NAME': 'my-cloud-name',
            'CLOUDINARY_API_KEY': 'my-api-key-123',
            'CLOUDINARY_API_SECRET': 'my-api-secret-456'
        }
        
        with patch.dict(os.environ, test_env):
            settings = Settings()
            
            assert settings.DATABASE_URL == test_env['DATABASE_URL']
            assert settings.SECRET_KEY == test_env['SECRET_KEY']
            assert settings.CLOUDINARY_CLOUD_NAME == test_env['CLOUDINARY_CLOUD_NAME']
            assert settings.CLOUDINARY_API_KEY == test_env['CLOUDINARY_API_KEY']
            assert settings.CLOUDINARY_API_SECRET == test_env['CLOUDINARY_API_SECRET']

    def test_settings_missing_required_database_url(self):
        """Test that missing DATABASE_URL raises validation error."""
        with patch.dict(os.environ, {
            'SECRET_KEY': 'test-secret-key',
            'CLOUDINARY_CLOUD_NAME': 'test-cloud',
            'CLOUDINARY_API_KEY': 'test-api-key',
            'CLOUDINARY_API_SECRET': 'test-api-secret'
        }, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                Settings()
            
            # Check that DATABASE_URL is mentioned in the error
            assert "DATABASE_URL" in str(exc_info.value)

    def test_settings_missing_required_secret_key(self):
        """Test that missing SECRET_KEY raises validation error."""
        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://test:test@localhost/test',
            'CLOUDINARY_CLOUD_NAME': 'test-cloud',
            'CLOUDINARY_API_KEY': 'test-api-key',
            'CLOUDINARY_API_SECRET': 'test-api-secret'
        }, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                Settings()
            
            assert "SECRET_KEY" in str(exc_info.value)

    def test_settings_missing_cloudinary_config(self):
        """Test that missing Cloudinary config raises validation error."""
        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://test:test@localhost/test',
            'SECRET_KEY': 'test-secret-key'
        }, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                Settings()
            
            error_str = str(exc_info.value)
            assert any(field in error_str for field in [
                "CLOUDINARY_CLOUD_NAME", 
                "CLOUDINARY_API_KEY", 
                "CLOUDINARY_API_SECRET"
            ])


class TestSettingsValidation:
    def test_settings_cors_origins_validation(self):
        """Test CORS origins URL validation."""
        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://test:test@localhost/test',
            'SECRET_KEY': 'test-secret-key',
            'CLOUDINARY_CLOUD_NAME': 'test-cloud',
            'CLOUDINARY_API_KEY': 'test-api-key',
            'CLOUDINARY_API_SECRET': 'test-api-secret'
        }):
            settings = Settings()
            
            # Should have valid URLs
            for origin in settings.BACKEND_CORS_ORIGINS:
                assert str(origin).startswith(('http://', 'https://'))

    def test_settings_algorithm_validation(self):
        """Test that JWT algorithm is set correctly."""
        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://test:test@localhost/test',
            'SECRET_KEY': 'test-secret-key',
            'CLOUDINARY_CLOUD_NAME': 'test-cloud',
            'CLOUDINARY_API_KEY': 'test-api-key',
            'CLOUDINARY_API_SECRET': 'test-api-secret'
        }):
            settings = Settings()
            
            assert settings.ALGORITHM == "HS256"
            assert isinstance(settings.ALGORITHM, str)

    def test_settings_token_expiry_times(self):
        """Test that token expiry times are positive integers."""
        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://test:test@localhost/test',
            'SECRET_KEY': 'test-secret-key',
            'CLOUDINARY_CLOUD_NAME': 'test-cloud',
            'CLOUDINARY_API_KEY': 'test-api-key',
            'CLOUDINARY_API_SECRET': 'test-api-secret'
        }):
            settings = Settings()
            
            assert isinstance(settings.ACCESS_TOKEN_EXPIRE_MINUTES, int)
            assert isinstance(settings.REFRESH_TOKEN_EXPIRE_MINUTES, int)
            assert settings.ACCESS_TOKEN_EXPIRE_MINUTES > 0
            assert settings.REFRESH_TOKEN_EXPIRE_MINUTES > 0
            assert settings.REFRESH_TOKEN_EXPIRE_MINUTES > settings.ACCESS_TOKEN_EXPIRE_MINUTES


class TestSettingsCustomization:
    def test_settings_can_override_defaults(self):
        """Test that default values can be overridden."""
        custom_env = {
            'DATABASE_URL': 'postgresql://test:test@localhost/test',
            'SECRET_KEY': 'test-secret-key',
            'CLOUDINARY_CLOUD_NAME': 'test-cloud',
            'CLOUDINARY_API_KEY': 'test-api-key',
            'CLOUDINARY_API_SECRET': 'test-api-secret'
        }
        
        with patch.dict(os.environ, custom_env):
            # Test overriding defaults through environment or direct instantiation
            settings = Settings(
                PROJECT_NAME="Custom Padel API",
                API_V1_STR="/api/v2",
                ACCESS_TOKEN_EXPIRE_MINUTES=30
            )
            
            assert settings.PROJECT_NAME == "Custom Padel API"
            assert settings.API_V1_STR == "/api/v2"
            assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30

    def test_settings_env_file_config(self):
        """Test that settings have env_file configuration."""
        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://test:test@localhost/test',
            'SECRET_KEY': 'test-secret-key',
            'CLOUDINARY_CLOUD_NAME': 'test-cloud',
            'CLOUDINARY_API_KEY': 'test-api-key',
            'CLOUDINARY_API_SECRET': 'test-api-secret'
        }):
            settings = Settings()
            
            # Check that model_config is properly set
            assert hasattr(settings, 'model_config')
            assert settings.model_config.env_file == ".env"
            assert settings.model_config.extra == 'ignore'


class TestSettingsTypes:
    def test_settings_field_types(self):
        """Test that all settings fields have correct types."""
        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://test:test@localhost/test',
            'SECRET_KEY': 'test-secret-key',
            'CLOUDINARY_CLOUD_NAME': 'test-cloud',
            'CLOUDINARY_API_KEY': 'test-api-key',
            'CLOUDINARY_API_SECRET': 'test-api-secret'
        }):
            settings = Settings()
            
            # String fields
            assert isinstance(settings.PROJECT_NAME, str)
            assert isinstance(settings.API_V1_STR, str)
            assert isinstance(settings.DATABASE_URL, str)
            assert isinstance(settings.SECRET_KEY, str)
            assert isinstance(settings.ALGORITHM, str)
            assert isinstance(settings.CLOUDINARY_CLOUD_NAME, str)
            assert isinstance(settings.CLOUDINARY_API_KEY, str)
            assert isinstance(settings.CLOUDINARY_API_SECRET, str)
            
            # Integer fields
            assert isinstance(settings.ACCESS_TOKEN_EXPIRE_MINUTES, int)
            assert isinstance(settings.REFRESH_TOKEN_EXPIRE_MINUTES, int)
            
            # List field
            assert isinstance(settings.BACKEND_CORS_ORIGINS, list)

    def test_settings_required_fields_not_empty(self):
        """Test that required fields are not empty when provided."""
        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://test:test@localhost/test',
            'SECRET_KEY': 'test-secret-key',
            'CLOUDINARY_CLOUD_NAME': 'test-cloud',
            'CLOUDINARY_API_KEY': 'test-api-key',
            'CLOUDINARY_API_SECRET': 'test-api-secret'
        }):
            settings = Settings()
            
            # Required fields should not be empty
            assert len(settings.DATABASE_URL.strip()) > 0
            assert len(settings.SECRET_KEY.strip()) > 0
            assert len(settings.CLOUDINARY_CLOUD_NAME.strip()) > 0
            assert len(settings.CLOUDINARY_API_KEY.strip()) > 0
            assert len(settings.CLOUDINARY_API_SECRET.strip()) > 0


class TestSettingsEdgeCases:
    def test_settings_with_special_characters(self):
        """Test settings with special characters in values."""
        special_env = {
            'DATABASE_URL': 'postgresql://user:p@ss!w0rd@localhost:5432/db-name',
            'SECRET_KEY': 'secret-key-with-$pecial-ch@rs!#123',
            'CLOUDINARY_CLOUD_NAME': 'cloud-name-with-dashes',
            'CLOUDINARY_API_KEY': 'api-key-123456789',
            'CLOUDINARY_API_SECRET': 'api-secret-with-$pecial-chars'
        }
        
        with patch.dict(os.environ, special_env):
            settings = Settings()
            
            assert settings.DATABASE_URL == special_env['DATABASE_URL']
            assert settings.SECRET_KEY == special_env['SECRET_KEY']
            assert settings.CLOUDINARY_CLOUD_NAME == special_env['CLOUDINARY_CLOUD_NAME']

    def test_settings_with_empty_cors_origins(self):
        """Test settings with empty CORS origins list."""
        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://test:test@localhost/test',
            'SECRET_KEY': 'test-secret-key',
            'CLOUDINARY_CLOUD_NAME': 'test-cloud',
            'CLOUDINARY_API_KEY': 'test-api-key',
            'CLOUDINARY_API_SECRET': 'test-api-secret'
        }):
            settings = Settings(BACKEND_CORS_ORIGINS=[])
            
            assert isinstance(settings.BACKEND_CORS_ORIGINS, list)
            assert len(settings.BACKEND_CORS_ORIGINS) == 0

    def test_settings_extreme_token_expiry_values(self):
        """Test settings with extreme token expiry values."""
        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://test:test@localhost/test',
            'SECRET_KEY': 'test-secret-key',
            'CLOUDINARY_CLOUD_NAME': 'test-cloud',
            'CLOUDINARY_API_KEY': 'test-api-key',
            'CLOUDINARY_API_SECRET': 'test-api-secret'
        }):
            # Test with very small values
            settings = Settings(
                ACCESS_TOKEN_EXPIRE_MINUTES=1,
                REFRESH_TOKEN_EXPIRE_MINUTES=2
            )
            
            assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 1
            assert settings.REFRESH_TOKEN_EXPIRE_MINUTES == 2
            
            # Test with large values
            settings = Settings(
                ACCESS_TOKEN_EXPIRE_MINUTES=60 * 24 * 365,  # 1 year
                REFRESH_TOKEN_EXPIRE_MINUTES=60 * 24 * 365 * 2  # 2 years
            )
            
            assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 60 * 24 * 365
            assert settings.REFRESH_TOKEN_EXPIRE_MINUTES == 60 * 24 * 365 * 2


class TestSettingsIntegration:
    def test_settings_singleton_behavior(self):
        """Test that settings behave consistently when imported."""
        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://test:test@localhost/test',
            'SECRET_KEY': 'test-secret-key',
            'CLOUDINARY_CLOUD_NAME': 'test-cloud',
            'CLOUDINARY_API_KEY': 'test-api-key',
            'CLOUDINARY_API_SECRET': 'test-api-secret'
        }):
            # Import the global settings instance
            from app.core.config import settings
            
            # Should have the same values as a new instance
            new_settings = Settings()
            
            assert settings.PROJECT_NAME == new_settings.PROJECT_NAME
            assert settings.API_V1_STR == new_settings.API_V1_STR
            assert settings.DATABASE_URL == new_settings.DATABASE_URL

    def test_settings_production_like_config(self):
        """Test settings with production-like configuration."""
        prod_env = {
            'DATABASE_URL': 'postgresql://produser:complexpassword@db.example.com:5432/proddb',
            'SECRET_KEY': 'very-long-and-complex-secret-key-for-production-use-123456789',
            'CLOUDINARY_CLOUD_NAME': 'production-cloud-name',
            'CLOUDINARY_API_KEY': '123456789012345',
            'CLOUDINARY_API_SECRET': 'production-secret-key-abcdef123456789'
        }
        
        with patch.dict(os.environ, prod_env):
            settings = Settings()
            
            # Should handle production-like values
            assert "produser" in settings.DATABASE_URL
            assert "proddb" in settings.DATABASE_URL
            assert len(settings.SECRET_KEY) > 20  # Production keys should be long
            assert "production" in settings.CLOUDINARY_CLOUD_NAME
            assert settings.CLOUDINARY_API_KEY.isdigit()  # API keys are often numeric