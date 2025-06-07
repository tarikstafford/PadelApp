import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Delay import of app-specific modules
# from app.models import User, Club, UserRole
# from app.database import Base
# from app.core.config import settings

@pytest.fixture(scope="function")
def db_session():
    """
    Create a new database session for each test function.
    Imports are moved inside to ensure env vars are set first.
    """
    from app.core.config import settings
    from app.database import Base
    # Import all models to ensure they are registered with Base's metadata
    from app.models import (
        User, Club, Court, Booking, Game, GamePlayer, UserRole, BookingStatus, GameType, GamePlayerStatus
    )

    engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

def test_create_club_admin_and_club(db_session):
    """
    Test creating a user with CLUB_ADMIN role and a club owned by them.
    """
    from app.models import User, Club, UserRole

    # Create a club admin user
    admin_user = User(
        email="admin@example.com",
        name="Admin User",
        hashed_password="a_very_secret_password",
        role=UserRole.CLUB_ADMIN
    )
    db_session.add(admin_user)
    db_session.commit()
    db_session.refresh(admin_user)

    assert admin_user.id is not None
    assert admin_user.role == UserRole.CLUB_ADMIN

    # Create a club owned by the admin
    new_club = Club(
        name="Test Padel Club",
        owner_id=admin_user.id
    )
    db_session.add(new_club)
    db_session.commit()
    db_session.refresh(new_club)

    assert new_club.id is not None
    assert new_club.owner_id == admin_user.id
    assert new_club.owner == admin_user
    assert admin_user.owned_club == new_club

def test_user_cascade_delete_owned_club(db_session):
    """
    Test that deleting a user also deletes their owned club due to cascade.
    """
    from app.models import User, Club, UserRole
    
    # Create a club admin user
    admin_user = User(
        email="admin_to_delete@example.com",
        name="Admin User to Delete",
        hashed_password="a_very_secret_password",
        role=UserRole.CLUB_ADMIN
    )
    db_session.add(admin_user)
    db_session.commit()
    db_session.refresh(admin_user)

    # Create a club owned by the admin
    new_club = Club(
        name="Club to be Deleted",
        owner_id=admin_user.id
    )
    db_session.add(new_club)
    db_session.commit()
    db_session.refresh(new_club)

    user_id = admin_user.id
    club_id = new_club.id

    # Delete the user
    db_session.delete(admin_user)
    db_session.commit()

    # Verify both user and club are deleted
    deleted_user = db_session.query(User).filter(User.id == user_id).first()
    deleted_club = db_session.query(Club).filter(Club.id == club_id).first()

    assert deleted_user is None
    assert deleted_club is None 