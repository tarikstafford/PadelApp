import pytest
import os

@pytest.fixture(autouse=True)
def set_test_environment_variables():
    """
    Set environment variables required for the test environment.
    This fixture will run automatically for all tests.
    """
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    os.environ["SECRET_KEY"] = "a_test_secret_key"
    yield
    # Clean up environment variables after tests run
    del os.environ["DATABASE_URL"]
    del os.environ["SECRET_KEY"] 