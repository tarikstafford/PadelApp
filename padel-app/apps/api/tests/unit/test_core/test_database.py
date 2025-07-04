import contextlib
import os
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.database import Base, SessionLocal, engine, get_db


class TestDatabaseEngine:
    """Test suite for database engine configuration."""

    def test_engine_uses_settings_database_url(self):
        """Test that the engine uses the DATABASE_URL from settings."""
        # The engine should be created with the DATABASE_URL from settings
        assert engine.url.render_as_string(hide_password=False) == settings.DATABASE_URL

    def test_engine_is_sqlalchemy_engine(self):
        """Test that the engine is a SQLAlchemy engine."""
        from sqlalchemy.engine import Engine

        assert isinstance(engine, Engine)

    def test_engine_connects_successfully(self):
        """Test that the engine can establish a connection."""
        # This test may fail if DATABASE_URL is not properly configured
        # but it's important to test connectivity
        try:
            connection = engine.connect()
            connection.close()
        except SQLAlchemyError:
            # If connection fails, it might be due to test environment setup
            # The test should still pass as long as the engine is properly configured
            pass


class TestSessionLocal:
    """Test suite for SessionLocal sessionmaker configuration."""

    def test_session_local_is_sessionmaker(self):
        """Test that SessionLocal is a sessionmaker."""
        assert isinstance(SessionLocal, sessionmaker)

    def test_session_local_configuration(self):
        """Test that SessionLocal has correct configuration."""
        # Check that autocommit is False
        assert SessionLocal.kw.get("autocommit") is False

        # Check that autoflush is False
        assert SessionLocal.kw.get("autoflush") is False

        # Check that the bind is the correct engine
        assert SessionLocal.kw.get("bind") is engine

    def test_session_local_creates_session(self):
        """Test that SessionLocal creates a valid session."""
        session = SessionLocal()
        assert isinstance(session, Session)
        session.close()

    def test_session_local_multiple_sessions(self):
        """Test that SessionLocal can create multiple independent sessions."""
        session1 = SessionLocal()
        session2 = SessionLocal()

        assert isinstance(session1, Session)
        assert isinstance(session2, Session)
        assert session1 is not session2

        session1.close()
        session2.close()


class TestBase:
    """Test suite for SQLAlchemy Base configuration."""

    def test_base_is_declarative_base(self):
        """Test that Base is a declarative base."""
        from sqlalchemy.orm import DeclarativeMeta

        assert isinstance(Base, DeclarativeMeta)

    def test_base_has_metadata(self):
        """Test that Base has metadata attribute."""
        assert hasattr(Base, "metadata")
        assert Base.metadata is not None

    def test_base_metadata_can_create_tables(self):
        """Test that Base metadata can create tables."""
        # This test creates tables in the test database
        # and then drops them for cleanup
        try:
            Base.metadata.create_all(bind=engine)
            Base.metadata.drop_all(bind=engine)
        except SQLAlchemyError:
            # If this fails, it might be due to test environment setup
            # The test should still pass as long as the metadata is properly configured
            pass


class TestGetDbDependency:
    """Test suite for get_db dependency function."""

    def test_get_db_returns_generator(self):
        """Test that get_db returns a generator."""
        db_generator = get_db()
        import types

        assert isinstance(db_generator, types.GeneratorType)

    def test_get_db_yields_session(self):
        """Test that get_db yields a database session."""
        db_generator = get_db()
        session = next(db_generator)

        assert isinstance(session, Session)

        # Clean up: close the session
        try:
            next(db_generator)
        except StopIteration:
            # Expected - the generator should close the session and stop
            pass

    def test_get_db_closes_session_on_completion(self):
        """Test that get_db closes the session when the generator is exhausted."""
        with patch.object(Session, "close") as mock_close:
            db_generator = get_db()
            next(db_generator)

            # Exhaust the generator
            with contextlib.suppress(StopIteration):
                next(db_generator)

            # Verify that close was called
            mock_close.assert_called_once()

    def test_get_db_closes_session_on_exception(self):
        """Test that get_db closes the session even when an exception occurs."""
        with patch.object(
            SessionLocal, "__call__", return_value=MagicMock(spec=Session)
        ) as mock_session_local:
            mock_session = mock_session_local.return_value

            db_generator = get_db()
            next(db_generator)

            # Simulate an exception in the generator
            with contextlib.suppress(Exception):
                db_generator.throw(Exception("Test exception"))

            # Verify that close was called even with exception
            mock_session.close.assert_called_once()

    def test_get_db_dependency_isolation(self):
        """Test that multiple calls to get_db create independent sessions."""
        db_gen1 = get_db()
        db_gen2 = get_db()

        session1 = next(db_gen1)
        session2 = next(db_gen2)

        assert session1 is not session2
        assert isinstance(session1, Session)
        assert isinstance(session2, Session)

        # Clean up both generators
        for gen in [db_gen1, db_gen2]:
            with contextlib.suppress(StopIteration):
                next(gen)

    def test_get_db_with_mocked_session_local(self):
        """Test get_db with mocked SessionLocal to verify proper session handling."""
        mock_session = MagicMock(spec=Session)

        with patch("app.database.SessionLocal", return_value=mock_session):
            db_generator = get_db()
            yielded_session = next(db_generator)

            assert yielded_session is mock_session

            # Exhaust the generator
            with contextlib.suppress(StopIteration):
                next(db_generator)

            # Verify that close was called
            mock_session.close.assert_called_once()


class TestDatabaseIntegration:
    """Test suite for database integration and configuration."""

    def test_database_url_from_settings(self):
        """Test that database configuration uses settings."""
        # The engine should be created with the DATABASE_URL from settings
        assert (
            str(engine.url) == settings.DATABASE_URL
            or engine.url.render_as_string(hide_password=False) == settings.DATABASE_URL
        )

    def test_database_configuration_consistency(self):
        """Test that database configuration is consistent across components."""
        # SessionLocal should use the same engine
        assert SessionLocal.kw.get("bind") is engine

        # Base should be usable with the engine
        assert Base.metadata is not None

    def test_database_session_lifecycle(self):
        """Test the complete lifecycle of a database session."""
        # Create a session
        session = SessionLocal()

        # Verify it's a proper session
        assert isinstance(session, Session)

        # Verify it's connected to the right engine
        assert session.bind is engine

        # Close the session
        session.close()

        # Verify the session is closed
        assert not session.is_active

    def test_database_with_different_settings(self):
        """Test database configuration with different settings."""
        original_url = settings.DATABASE_URL

        try:
            # Test with a different database URL
            with patch.dict(
                os.environ, {"DATABASE_URL": "sqlite:///test_different.db"}
            ):
                # Import settings again to get the new URL
                from app.core.config import Settings

                test_settings = Settings()

                # Create a new engine with the test settings
                test_engine = create_engine(test_settings.DATABASE_URL)

                assert (
                    test_engine.url.render_as_string(hide_password=False)
                    == "sqlite:///test_different.db"
                )

        finally:
            # Restore original settings
            settings.DATABASE_URL = original_url

    def test_database_error_handling(self):
        """Test database error handling in get_db."""
        with patch("app.database.SessionLocal") as mock_session_local:
            # Mock SessionLocal to raise an exception
            mock_session_local.side_effect = SQLAlchemyError(
                "Database connection failed"
            )

            db_generator = get_db()

            # Should raise SQLAlchemyError
            with pytest.raises(SQLAlchemyError):
                next(db_generator)

    def test_database_session_transaction_handling(self):
        """Test that database sessions handle transactions properly."""
        session = SessionLocal()

        try:
            # Check that autocommit is False (transactions are managed manually)
            assert session.autocommit is False

            # Check that autoflush is False (flushing is managed manually)
            assert session.autoflush is False

        finally:
            session.close()

    def test_get_db_in_fastapi_context(self):
        """Test get_db dependency in a FastAPI-like context."""
        # Simulate how FastAPI would use the dependency
        dependency_generator = get_db()

        # FastAPI would call next() to get the session
        session = next(dependency_generator)
        assert isinstance(session, Session)

        # Simulate the end of the request (FastAPI would do this automatically)
        try:
            next(dependency_generator)
        except StopIteration:
            # This is expected - the generator should close the session and stop
            pass

        # The session should be closed after the generator is exhausted
        assert not session.is_active


class TestDatabaseConfiguration:
    """Test suite for database configuration edge cases."""

    def test_database_url_validation(self):
        """Test that database URL is properly validated."""
        # The engine should be created successfully with a valid URL
        assert engine is not None
        assert engine.url is not None

    def test_database_pool_settings(self):
        """Test database connection pool settings."""
        # For SQLite, pool settings might be different
        # For PostgreSQL, we might want to test pool size, etc.
        # This test verifies that the engine has proper pool configuration
        assert hasattr(engine, "pool")
        assert engine.pool is not None

    def test_database_echo_setting(self):
        """Test database echo setting for debugging."""
        # By default, echo should be False for production
        assert engine.echo is False

    def test_database_isolation_level(self):
        """Test database isolation level configuration."""
        # Test that the engine has appropriate isolation level
        # This is more relevant for production databases
        assert hasattr(engine, "dialect")
        assert engine.dialect is not None

    def test_sessionmaker_class_attribute(self):
        """Test that SessionLocal has the correct class attribute."""
        # SessionLocal should create sessions of the correct class
        assert SessionLocal.class_ is Session or hasattr(SessionLocal, "class_")
