import pytest
from faker import Faker
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import crud
from app.models.club import Club
from app.models.user import User
from app.schemas.club_admin_schemas import ClubAdminCreate
from app.schemas.club_schemas import ClubCreate
from app.schemas.user_schemas import UserCreate

fake = Faker()


class TestClubAdminCRUD:
    """Test suite for ClubAdmin CRUD operations"""

    @pytest.fixture
    def test_owner(self, db_session: Session) -> User:
        """Create a test user to be the club owner"""
        user_data = UserCreate(
            email=fake.email(), password="testpass123", full_name=fake.name()
        )
        return crud.user_crud.create_user(db_session, user_data)

    @pytest.fixture
    def test_user(self, db_session: Session) -> User:
        """Create a test user to be a club admin"""
        user_data = UserCreate(
            email=fake.email(), password="testpass123", full_name=fake.name()
        )
        return crud.user_crud.create_user(db_session, user_data)

    @pytest.fixture
    def test_club(self, db_session: Session, test_owner: User) -> Club:
        """Create a test club"""
        club_data = ClubCreate(
            name=fake.company(), city=fake.city(), owner_id=test_owner.id
        )
        return crud.club_crud.create_club(db_session, club_data)

    def test_create_club_admin_success(
        self, db_session: Session, test_user: User, test_club: Club
    ):
        """Test successful club admin creation"""
        admin_data = ClubAdminCreate(user_id=test_user.id, club_id=test_club.id)

        created_admin = crud.club_admin_crud.create_club_admin(db_session, admin_data)

        assert created_admin.id is not None
        assert created_admin.user_id == test_user.id
        assert created_admin.club_id == test_club.id

    def test_create_club_admin_with_relationships(
        self, db_session: Session, test_user: User, test_club: Club
    ):
        """Test club admin creation includes relationships"""
        admin_data = ClubAdminCreate(user_id=test_user.id, club_id=test_club.id)

        created_admin = crud.club_admin_crud.create_club_admin(db_session, admin_data)

        # Check that relationships exist
        assert hasattr(created_admin, "user")
        assert hasattr(created_admin, "club")
        assert created_admin.user is not None
        assert created_admin.club is not None

    def test_create_club_admin_duplicate_constraint(
        self, db_session: Session, test_user: User, test_club: Club
    ):
        """Test that creating duplicate club admin raises constraint error"""
        admin_data = ClubAdminCreate(user_id=test_user.id, club_id=test_club.id)

        # Create first admin
        crud.club_admin_crud.create_club_admin(db_session, admin_data)

        # Try to create duplicate - should raise integrity error
        with pytest.raises(IntegrityError):
            crud.club_admin_crud.create_club_admin(db_session, admin_data)

    def test_create_club_admin_invalid_user_id(
        self, db_session: Session, test_club: Club
    ):
        """Test club admin creation with invalid user ID"""
        admin_data = ClubAdminCreate(
            user_id=99999, club_id=test_club.id  # Non-existent user
        )

        with pytest.raises(IntegrityError):
            crud.club_admin_crud.create_club_admin(db_session, admin_data)

    def test_create_club_admin_invalid_club_id(
        self, db_session: Session, test_user: User
    ):
        """Test club admin creation with invalid club ID"""
        admin_data = ClubAdminCreate(
            user_id=test_user.id, club_id=99999  # Non-existent club
        )

        with pytest.raises(IntegrityError):
            crud.club_admin_crud.create_club_admin(db_session, admin_data)

    def test_get_club_admin_success(
        self, db_session: Session, test_user: User, test_club: Club
    ):
        """Test successful club admin retrieval"""
        admin_data = ClubAdminCreate(user_id=test_user.id, club_id=test_club.id)
        created_admin = crud.club_admin_crud.create_club_admin(db_session, admin_data)

        retrieved_admin = crud.club_admin_crud.get_club_admin(
            db_session, test_user.id, test_club.id
        )

        assert retrieved_admin is not None
        assert retrieved_admin.id == created_admin.id
        assert retrieved_admin.user_id == test_user.id
        assert retrieved_admin.club_id == test_club.id

    def test_get_club_admin_not_found(
        self, db_session: Session, test_user: User, test_club: Club
    ):
        """Test club admin retrieval when record doesn't exist"""
        retrieved_admin = crud.club_admin_crud.get_club_admin(
            db_session, test_user.id, test_club.id
        )

        assert retrieved_admin is None

    def test_get_club_admin_wrong_user_id(
        self, db_session: Session, test_user: User, test_club: Club
    ):
        """Test club admin retrieval with wrong user ID"""
        admin_data = ClubAdminCreate(user_id=test_user.id, club_id=test_club.id)
        crud.club_admin_crud.create_club_admin(db_session, admin_data)

        retrieved_admin = crud.club_admin_crud.get_club_admin(
            db_session, 99999, test_club.id
        )

        assert retrieved_admin is None

    def test_get_club_admin_wrong_club_id(
        self, db_session: Session, test_user: User, test_club: Club
    ):
        """Test club admin retrieval with wrong club ID"""
        admin_data = ClubAdminCreate(user_id=test_user.id, club_id=test_club.id)
        crud.club_admin_crud.create_club_admin(db_session, admin_data)

        retrieved_admin = crud.club_admin_crud.get_club_admin(
            db_session, test_user.id, 99999
        )

        assert retrieved_admin is None

    def test_get_club_admins_by_club(
        self, db_session: Session, test_owner: User, test_club: Club
    ):
        """Test getting all admins for a club"""
        # Create multiple users
        user1_data = UserCreate(
            email=fake.email(), password="testpass123", full_name=fake.name()
        )
        user1 = crud.user_crud.create_user(db_session, user1_data)

        user2_data = UserCreate(
            email=fake.email(), password="testpass123", full_name=fake.name()
        )
        user2 = crud.user_crud.create_user(db_session, user2_data)

        # Create club admins
        admin1_data = ClubAdminCreate(user_id=user1.id, club_id=test_club.id)
        admin1 = crud.club_admin_crud.create_club_admin(db_session, admin1_data)

        admin2_data = ClubAdminCreate(user_id=user2.id, club_id=test_club.id)
        admin2 = crud.club_admin_crud.create_club_admin(db_session, admin2_data)

        # Get admins for the club
        admins = crud.club_admin_crud.get_club_admins_by_club(db_session, test_club.id)

        assert len(admins) == 2
        admin_ids = [admin.id for admin in admins]
        assert admin1.id in admin_ids
        assert admin2.id in admin_ids

    def test_get_club_admins_by_club_empty(self, db_session: Session, test_club: Club):
        """Test getting admins for a club with no admins"""
        admins = crud.club_admin_crud.get_club_admins_by_club(db_session, test_club.id)

        assert len(admins) == 0

    def test_get_club_admins_by_club_different_clubs(
        self, db_session: Session, test_owner: User, test_user: User
    ):
        """Test that get_club_admins_by_club only returns admins for the specified club"""
        # Create two clubs
        club1_data = ClubCreate(
            name=fake.company(), city=fake.city(), owner_id=test_owner.id
        )
        club1 = crud.club_crud.create_club(db_session, club1_data)

        club2_data = ClubCreate(
            name=fake.company(), city=fake.city(), owner_id=test_owner.id
        )
        club2 = crud.club_crud.create_club(db_session, club2_data)

        # Create admins for both clubs
        admin1_data = ClubAdminCreate(user_id=test_user.id, club_id=club1.id)
        admin1 = crud.club_admin_crud.create_club_admin(db_session, admin1_data)

        admin2_data = ClubAdminCreate(user_id=test_user.id, club_id=club2.id)
        crud.club_admin_crud.create_club_admin(db_session, admin2_data)

        # Get admins for club1 only
        admins = crud.club_admin_crud.get_club_admins_by_club(db_session, club1.id)

        assert len(admins) == 1
        assert admins[0].id == admin1.id
        assert admins[0].club_id == club1.id

    def test_get_club_admins_by_user(
        self, db_session: Session, test_owner: User, test_user: User
    ):
        """Test getting all club admin entries for a user"""
        # Create two clubs
        club1_data = ClubCreate(
            name=fake.company(), city=fake.city(), owner_id=test_owner.id
        )
        club1 = crud.club_crud.create_club(db_session, club1_data)

        club2_data = ClubCreate(
            name=fake.company(), city=fake.city(), owner_id=test_owner.id
        )
        club2 = crud.club_crud.create_club(db_session, club2_data)

        # Make test_user admin of both clubs
        admin1_data = ClubAdminCreate(user_id=test_user.id, club_id=club1.id)
        admin1 = crud.club_admin_crud.create_club_admin(db_session, admin1_data)

        admin2_data = ClubAdminCreate(user_id=test_user.id, club_id=club2.id)
        admin2 = crud.club_admin_crud.create_club_admin(db_session, admin2_data)

        # Get all admin entries for the user
        admins = crud.club_admin_crud.get_club_admins_by_user(db_session, test_user.id)

        assert len(admins) == 2
        admin_ids = [admin.id for admin in admins]
        assert admin1.id in admin_ids
        assert admin2.id in admin_ids

    def test_get_club_admins_by_user_empty(self, db_session: Session, test_user: User):
        """Test getting admin entries for a user with no admin roles"""
        admins = crud.club_admin_crud.get_club_admins_by_user(db_session, test_user.id)

        assert len(admins) == 0

    def test_get_club_admins_by_user_different_users(
        self, db_session: Session, test_owner: User, test_club: Club
    ):
        """Test that get_club_admins_by_user only returns entries for the specified user"""
        # Create two users
        user1_data = UserCreate(
            email=fake.email(), password="testpass123", full_name=fake.name()
        )
        user1 = crud.user_crud.create_user(db_session, user1_data)

        user2_data = UserCreate(
            email=fake.email(), password="testpass123", full_name=fake.name()
        )
        user2 = crud.user_crud.create_user(db_session, user2_data)

        # Make both users admins of the club
        admin1_data = ClubAdminCreate(user_id=user1.id, club_id=test_club.id)
        admin1 = crud.club_admin_crud.create_club_admin(db_session, admin1_data)

        admin2_data = ClubAdminCreate(user_id=user2.id, club_id=test_club.id)
        crud.club_admin_crud.create_club_admin(db_session, admin2_data)

        # Get admin entries for user1 only
        admins = crud.club_admin_crud.get_club_admins_by_user(db_session, user1.id)

        assert len(admins) == 1
        assert admins[0].id == admin1.id
        assert admins[0].user_id == user1.id

    def test_remove_club_admin_success(
        self, db_session: Session, test_user: User, test_club: Club
    ):
        """Test successful club admin removal"""
        admin_data = ClubAdminCreate(user_id=test_user.id, club_id=test_club.id)
        created_admin = crud.club_admin_crud.create_club_admin(db_session, admin_data)

        # Remove the admin
        removed_admin = crud.club_admin_crud.remove_club_admin(
            db_session, test_user.id, test_club.id
        )

        assert removed_admin is not None
        assert removed_admin.id == created_admin.id

        # Verify it's actually removed
        retrieved_admin = crud.club_admin_crud.get_club_admin(
            db_session, test_user.id, test_club.id
        )
        assert retrieved_admin is None

    def test_remove_club_admin_not_found(
        self, db_session: Session, test_user: User, test_club: Club
    ):
        """Test removing club admin that doesn't exist"""
        removed_admin = crud.club_admin_crud.remove_club_admin(
            db_session, test_user.id, test_club.id
        )

        assert removed_admin is None

    def test_remove_club_admin_wrong_user_id(
        self, db_session: Session, test_user: User, test_club: Club
    ):
        """Test removing club admin with wrong user ID"""
        admin_data = ClubAdminCreate(user_id=test_user.id, club_id=test_club.id)
        crud.club_admin_crud.create_club_admin(db_session, admin_data)

        # Try to remove with wrong user ID
        removed_admin = crud.club_admin_crud.remove_club_admin(
            db_session, 99999, test_club.id
        )

        assert removed_admin is None

        # Verify original admin still exists
        retrieved_admin = crud.club_admin_crud.get_club_admin(
            db_session, test_user.id, test_club.id
        )
        assert retrieved_admin is not None

    def test_remove_club_admin_wrong_club_id(
        self, db_session: Session, test_user: User, test_club: Club
    ):
        """Test removing club admin with wrong club ID"""
        admin_data = ClubAdminCreate(user_id=test_user.id, club_id=test_club.id)
        crud.club_admin_crud.create_club_admin(db_session, admin_data)

        # Try to remove with wrong club ID
        removed_admin = crud.club_admin_crud.remove_club_admin(
            db_session, test_user.id, 99999
        )

        assert removed_admin is None

        # Verify original admin still exists
        retrieved_admin = crud.club_admin_crud.get_club_admin(
            db_session, test_user.id, test_club.id
        )
        assert retrieved_admin is not None

    def test_club_admin_model_constraints(
        self, db_session: Session, test_user: User, test_club: Club
    ):
        """Test that club admin model enforces unique constraint"""
        admin_data = ClubAdminCreate(user_id=test_user.id, club_id=test_club.id)

        # Create first admin
        crud.club_admin_crud.create_club_admin(db_session, admin_data)

        # Try to create duplicate - should raise constraint error
        with pytest.raises(IntegrityError):
            crud.club_admin_crud.create_club_admin(db_session, admin_data)

    def test_club_admin_model_relationships(
        self, db_session: Session, test_user: User, test_club: Club
    ):
        """Test that club admin model has correct relationships"""
        admin_data = ClubAdminCreate(user_id=test_user.id, club_id=test_club.id)
        created_admin = crud.club_admin_crud.create_club_admin(db_session, admin_data)

        # Check relationships exist
        assert hasattr(created_admin, "user")
        assert hasattr(created_admin, "club")

        # Check relationship data
        assert created_admin.user.id == test_user.id
        assert created_admin.club.id == test_club.id

    def test_club_admin_repr(
        self, db_session: Session, test_user: User, test_club: Club
    ):
        """Test club admin string representation"""
        admin_data = ClubAdminCreate(user_id=test_user.id, club_id=test_club.id)
        created_admin = crud.club_admin_crud.create_club_admin(db_session, admin_data)

        admin_repr = repr(created_admin)
        assert "ClubAdmin(user_id=" in admin_repr
        assert f"user_id={test_user.id}" in admin_repr
        assert f"club_id={test_club.id}" in admin_repr

    def test_club_admin_cascade_delete_user(
        self, db_session: Session, test_user: User, test_club: Club
    ):
        """Test that deleting a user removes their club admin entries"""
        admin_data = ClubAdminCreate(user_id=test_user.id, club_id=test_club.id)
        crud.club_admin_crud.create_club_admin(db_session, admin_data)

        # Delete the user
        db_session.delete(test_user)
        db_session.commit()

        # Check that admin entry is also deleted
        retrieved_admin = crud.club_admin_crud.get_club_admin(
            db_session, test_user.id, test_club.id
        )
        assert retrieved_admin is None

    def test_club_admin_cascade_delete_club(
        self, db_session: Session, test_user: User, test_club: Club
    ):
        """Test that deleting a club removes its admin entries"""
        admin_data = ClubAdminCreate(user_id=test_user.id, club_id=test_club.id)
        crud.club_admin_crud.create_club_admin(db_session, admin_data)

        # Delete the club
        db_session.delete(test_club)
        db_session.commit()

        # Check that admin entry is also deleted
        retrieved_admin = crud.club_admin_crud.get_club_admin(
            db_session, test_user.id, test_club.id
        )
        assert retrieved_admin is None

    def test_multiple_admins_same_club(
        self, db_session: Session, test_owner: User, test_club: Club
    ):
        """Test that multiple users can be admins of the same club"""
        # Create multiple users
        users = []
        for _i in range(3):
            user_data = UserCreate(
                email=fake.email(), password="testpass123", full_name=fake.name()
            )
            user = crud.user_crud.create_user(db_session, user_data)
            users.append(user)

        # Make all users admins of the club
        admins = []
        for user in users:
            admin_data = ClubAdminCreate(user_id=user.id, club_id=test_club.id)
            admin = crud.club_admin_crud.create_club_admin(db_session, admin_data)
            admins.append(admin)

        # Verify all admins exist
        club_admins = crud.club_admin_crud.get_club_admins_by_club(
            db_session, test_club.id
        )
        assert len(club_admins) == 3

        admin_user_ids = [admin.user_id for admin in club_admins]
        for user in users:
            assert user.id in admin_user_ids

    def test_multiple_clubs_same_user(
        self, db_session: Session, test_owner: User, test_user: User
    ):
        """Test that a user can be admin of multiple clubs"""
        # Create multiple clubs
        clubs = []
        for _i in range(3):
            club_data = ClubCreate(
                name=fake.company(), city=fake.city(), owner_id=test_owner.id
            )
            club = crud.club_crud.create_club(db_session, club_data)
            clubs.append(club)

        # Make user admin of all clubs
        admins = []
        for club in clubs:
            admin_data = ClubAdminCreate(user_id=test_user.id, club_id=club.id)
            admin = crud.club_admin_crud.create_club_admin(db_session, admin_data)
            admins.append(admin)

        # Verify all admin entries exist
        user_admins = crud.club_admin_crud.get_club_admins_by_user(
            db_session, test_user.id
        )
        assert len(user_admins) == 3

        admin_club_ids = [admin.club_id for admin in user_admins]
        for club in clubs:
            assert club.id in admin_club_ids

    def test_club_admin_edge_cases(
        self, db_session: Session, test_user: User, test_club: Club
    ):
        """Test edge cases for club admin operations"""
        # Test with non-existent user and club IDs
        non_existent_user_id = 99999
        non_existent_club_id = 88888

        # Test get operations with non-existent IDs
        admin = crud.club_admin_crud.get_club_admin(
            db_session, non_existent_user_id, test_club.id
        )
        assert admin is None

        admin = crud.club_admin_crud.get_club_admin(
            db_session, test_user.id, non_existent_club_id
        )
        assert admin is None

        # Test list operations with non-existent IDs
        admins = crud.club_admin_crud.get_club_admins_by_user(
            db_session, non_existent_user_id
        )
        assert len(admins) == 0

        admins = crud.club_admin_crud.get_club_admins_by_club(
            db_session, non_existent_club_id
        )
        assert len(admins) == 0

        # Test remove operations with non-existent IDs
        removed = crud.club_admin_crud.remove_club_admin(
            db_session, non_existent_user_id, test_club.id
        )
        assert removed is None

        removed = crud.club_admin_crud.remove_club_admin(
            db_session, test_user.id, non_existent_club_id
        )
        assert removed is None
