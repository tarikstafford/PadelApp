import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Set environment variables for testing BEFORE any other imports
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "test_secret"
os.environ["CLOUDINARY_CLOUD_NAME"] = "test"
os.environ["CLOUDINARY_API_KEY"] = "test"
os.environ["CLOUDINARY_API_SECRET"] = "test"

# Now import app modules
from app import crud, models, schemas
from app.database import Base, get_db
from app.main import app

# Database engine and session for testing
engine = create_engine(
    os.environ["DATABASE_URL"],
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Override the get_db dependency for the FastAPI app
def override_get_db():
    database = TestingSessionLocal()
    try:
        yield database
    finally:
        database.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def db_session(client: TestClient):
    """
    Provides a transactional database session for each test function.
    This also creates and drops tables for each test, ensuring isolation.
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def client():
    """
    Provides a TestClient for the module.
    """
    with TestClient(app) as c:
        yield c


@pytest.fixture
def test_user(db_session: Session) -> models.User:
    """
    Create a test user in the database.
    """
    user_in = schemas.UserCreate(
        email="test@example.com",
        password="password123",
        full_name="Test User",
        phone_number="1234567890",
    )
    return crud.user_crud.create_user(db_session, user_in)


@pytest.fixture
def user_auth_headers(client: TestClient, test_user: models.User) -> dict:
    """
    Get authentication headers for a test user.
    """
    response = client.post(
        "/api/v1/auth/login",
        data={"username": test_user.email, "password": "password123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
