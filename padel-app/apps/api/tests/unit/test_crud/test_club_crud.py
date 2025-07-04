import pytest
from sqlalchemy.orm import Session
from faker import Faker
from datetime import time
from unittest.mock import Mock, patch

from app import crud
from app.models.club import Club
from app.models.user import User
from app.schemas.club_schemas import ClubCreate, ClubUpdate
from app.schemas.user_schemas import UserCreate

fake = Faker()


class TestClubCRUD:
    """Test suite for Club CRUD operations"""

    @pytest.fixture
    def test_owner(self, db_session: Session) -> User:
        """Create a test user to be the club owner"""
        user_data = UserCreate(
            email=fake.email(),
            password="testpass123",
            full_name=fake.name()
        )
        return crud.user_crud.create_user(db_session, user_data)

    def test_create_club_success(self, db_session: Session, test_owner: User):
        """Test successful club creation"""
        club_data = ClubCreate(
            name=fake.company(),
            description=fake.text(max_nb_chars=200),
            address=fake.address(),
            city=fake.city(),
            postal_code=fake.postcode(),
            phone=fake.phone_number(),
            email=fake.email(),
            opening_time=time(6, 0),
            closing_time=time(23, 0),
            amenities="Parking, Locker rooms, Pro shop",
            image_url="https://example.com/image.jpg",
            owner_id=test_owner.id
        )
        
        created_club = crud.club_crud.create_club(db_session, club_data)
        
        assert created_club.id is not None
        assert created_club.name == club_data.name
        assert created_club.description == club_data.description
        assert created_club.address == club_data.address
        assert created_club.city == club_data.city
        assert created_club.postal_code == club_data.postal_code
        assert created_club.phone == club_data.phone
        assert created_club.email == club_data.email
        assert created_club.opening_time == club_data.opening_time
        assert created_club.closing_time == club_data.closing_time
        assert created_club.amenities == club_data.amenities
        assert created_club.image_url == club_data.image_url
        assert created_club.owner_id == test_owner.id

    def test_create_club_minimal_data(self, db_session: Session, test_owner: User):
        """Test club creation with minimal required data"""
        club_data = ClubCreate(
            name=fake.company(),
            owner_id=test_owner.id
        )
        
        created_club = crud.club_crud.create_club(db_session, club_data)
        
        assert created_club.id is not None
        assert created_club.name == club_data.name
        assert created_club.owner_id == test_owner.id
        assert created_club.description is None
        assert created_club.address is None
        assert created_club.city is None
        assert created_club.postal_code is None
        assert created_club.phone is None
        assert created_club.email is None
        assert created_club.opening_time is None
        assert created_club.closing_time is None
        assert created_club.amenities is None
        assert created_club.image_url is None

    def test_create_club_with_time_fields(self, db_session: Session, test_owner: User):
        """Test club creation with specific time fields"""
        club_data = ClubCreate(
            name=fake.company(),
            opening_time=time(7, 30),
            closing_time=time(22, 30),
            owner_id=test_owner.id
        )
        
        created_club = crud.club_crud.create_club(db_session, club_data)
        
        assert created_club.opening_time == time(7, 30)
        assert created_club.closing_time == time(22, 30)

    def test_get_club_by_id_success(self, db_session: Session, test_owner: User):
        """Test successful club retrieval by ID"""
        club_data = ClubCreate(
            name=fake.company(),
            city=fake.city(),
            owner_id=test_owner.id
        )
        created_club = crud.club_crud.create_club(db_session, club_data)
        
        retrieved_club = crud.club_crud.get_club(db_session, created_club.id)
        
        assert retrieved_club is not None
        assert retrieved_club.id == created_club.id
        assert retrieved_club.name == created_club.name
        assert retrieved_club.city == created_club.city
        assert retrieved_club.owner_id == test_owner.id

    def test_get_club_by_id_not_found(self, db_session: Session):
        """Test club retrieval with non-existent ID"""
        non_existent_id = 99999
        
        retrieved_club = crud.club_crud.get_club(db_session, non_existent_id)
        
        assert retrieved_club is None

    def test_get_clubs_basic(self, db_session: Session, test_owner: User):
        """Test getting list of clubs"""
        # Create multiple clubs
        club1_data = ClubCreate(
            name="Club Alpha",
            city="New York",
            owner_id=test_owner.id
        )
        club1 = crud.club_crud.create_club(db_session, club1_data)
        
        club2_data = ClubCreate(
            name="Club Beta",
            city="Los Angeles",
            owner_id=test_owner.id
        )
        club2 = crud.club_crud.create_club(db_session, club2_data)
        
        clubs = crud.club_crud.get_clubs(db_session)
        
        assert len(clubs) == 2
        club_ids = [club.id for club in clubs]
        assert club1.id in club_ids
        assert club2.id in club_ids

    def test_get_clubs_with_pagination(self, db_session: Session, test_owner: User):
        """Test clubs retrieval with pagination"""
        # Create multiple clubs
        clubs = []
        for i in range(5):
            club_data = ClubCreate(
                name=f"Club {i}",
                city=fake.city(),
                owner_id=test_owner.id
            )
            club = crud.club_crud.create_club(db_session, club_data)
            clubs.append(club)
        
        # Test pagination
        page1 = crud.club_crud.get_clubs(db_session, skip=0, limit=2)
        page2 = crud.club_crud.get_clubs(db_session, skip=2, limit=2)
        
        assert len(page1) == 2
        assert len(page2) == 2
        
        # Check that pages don't overlap
        page1_ids = [club.id for club in page1]
        page2_ids = [club.id for club in page2]
        assert len(set(page1_ids).intersection(set(page2_ids))) == 0

    def test_get_clubs_with_name_filter(self, db_session: Session, test_owner: User):
        """Test clubs retrieval with name filtering"""
        # Create clubs with different names
        club1_data = ClubCreate(
            name="Tennis Club Alpha",
            city="New York",
            owner_id=test_owner.id
        )
        club1 = crud.club_crud.create_club(db_session, club1_data)
        
        club2_data = ClubCreate(
            name="Padel Club Beta",
            city="Los Angeles",
            owner_id=test_owner.id
        )
        club2 = crud.club_crud.create_club(db_session, club2_data)
        
        club3_data = ClubCreate(
            name="Sports Center Gamma",
            city="Chicago",
            owner_id=test_owner.id
        )
        club3 = crud.club_crud.create_club(db_session, club3_data)
        
        # Filter by "Club"
        clubs = crud.club_crud.get_clubs(db_session, name="Club")
        
        assert len(clubs) == 2
        club_names = [club.name for club in clubs]
        assert "Tennis Club Alpha" in club_names
        assert "Padel Club Beta" in club_names
        assert "Sports Center Gamma" not in club_names

    def test_get_clubs_with_city_filter(self, db_session: Session, test_owner: User):
        """Test clubs retrieval with city filtering"""
        # Create clubs in different cities
        club1_data = ClubCreate(
            name="Club A",
            city="New York",
            owner_id=test_owner.id
        )
        club1 = crud.club_crud.create_club(db_session, club1_data)
        
        club2_data = ClubCreate(
            name="Club B",
            city="New York",
            owner_id=test_owner.id
        )
        club2 = crud.club_crud.create_club(db_session, club2_data)
        
        club3_data = ClubCreate(
            name="Club C",
            city="Los Angeles",
            owner_id=test_owner.id
        )
        club3 = crud.club_crud.create_club(db_session, club3_data)
        
        # Filter by city
        clubs = crud.club_crud.get_clubs(db_session, city="New York")
        
        assert len(clubs) == 2
        club_names = [club.name for club in clubs]
        assert "Club A" in club_names
        assert "Club B" in club_names
        assert "Club C" not in club_names

    def test_get_clubs_case_insensitive_filtering(self, db_session: Session, test_owner: User):
        """Test that name and city filtering is case insensitive"""
        club_data = ClubCreate(
            name="Elite Tennis Club",
            city="New York",
            owner_id=test_owner.id
        )
        club = crud.club_crud.create_club(db_session, club_data)
        
        # Test case insensitive name filtering
        clubs_lower = crud.club_crud.get_clubs(db_session, name="elite")
        clubs_upper = crud.club_crud.get_clubs(db_session, name="ELITE")
        clubs_mixed = crud.club_crud.get_clubs(db_session, name="ElItE")
        
        assert len(clubs_lower) == 1
        assert len(clubs_upper) == 1
        assert len(clubs_mixed) == 1
        
        # Test case insensitive city filtering
        clubs_city_lower = crud.club_crud.get_clubs(db_session, city="new york")
        clubs_city_upper = crud.club_crud.get_clubs(db_session, city="NEW YORK")
        
        assert len(clubs_city_lower) == 1
        assert len(clubs_city_upper) == 1

    def test_get_clubs_with_sorting(self, db_session: Session, test_owner: User):
        """Test clubs retrieval with sorting"""
        # Create clubs with different names
        club1_data = ClubCreate(
            name="Zebra Club",
            city="New York",
            owner_id=test_owner.id
        )
        club1 = crud.club_crud.create_club(db_session, club1_data)
        
        club2_data = ClubCreate(
            name="Alpha Club",
            city="Boston",
            owner_id=test_owner.id
        )
        club2 = crud.club_crud.create_club(db_session, club2_data)
        
        # Test sorting by name ascending
        clubs_asc = crud.club_crud.get_clubs(db_session, sort_by="name", sort_desc=False)
        assert clubs_asc[0].name == "Alpha Club"
        assert clubs_asc[1].name == "Zebra Club"
        
        # Test sorting by name descending
        clubs_desc = crud.club_crud.get_clubs(db_session, sort_by="name", sort_desc=True)
        assert clubs_desc[0].name == "Zebra Club"
        assert clubs_desc[1].name == "Alpha Club"
        
        # Test sorting by city
        clubs_city = crud.club_crud.get_clubs(db_session, sort_by="city", sort_desc=False)
        assert clubs_city[0].city == "Boston"
        assert clubs_city[1].city == "New York"

    def test_get_clubs_invalid_sort_field(self, db_session: Session, test_owner: User):
        """Test clubs retrieval with invalid sort field falls back to default"""
        club_data = ClubCreate(
            name="Test Club",
            owner_id=test_owner.id
        )
        club = crud.club_crud.create_club(db_session, club_data)
        
        # Use invalid sort field
        clubs = crud.club_crud.get_clubs(db_session, sort_by="invalid_field")
        
        # Should still return results, sorted by ID (default)
        assert len(clubs) == 1
        assert clubs[0].id == club.id

    def test_update_club_success(self, db_session: Session, test_owner: User):
        """Test successful club update"""
        # Create club
        club_data = ClubCreate(
            name="Original Name",
            city="Original City",
            owner_id=test_owner.id
        )
        created_club = crud.club_crud.create_club(db_session, club_data)
        
        # Update club
        update_data = ClubUpdate(
            name="Updated Name",
            city="Updated City",
            description="Updated description",
            phone="555-0123"
        )
        
        updated_club = crud.club_crud.update_club(db_session, created_club, update_data)
        
        assert updated_club.id == created_club.id
        assert updated_club.name == "Updated Name"
        assert updated_club.city == "Updated City"
        assert updated_club.description == "Updated description"
        assert updated_club.phone == "555-0123"
        assert updated_club.owner_id == test_owner.id  # Should not change

    def test_update_club_partial_update(self, db_session: Session, test_owner: User):
        """Test partial club update only changes specified fields"""
        # Create club
        club_data = ClubCreate(
            name="Original Name",
            city="Original City",
            description="Original description",
            owner_id=test_owner.id
        )
        created_club = crud.club_crud.create_club(db_session, club_data)
        
        # Update only name
        update_data = ClubUpdate(name="Updated Name")
        
        updated_club = crud.club_crud.update_club(db_session, created_club, update_data)
        
        assert updated_club.name == "Updated Name"
        assert updated_club.city == "Original City"  # Should not change
        assert updated_club.description == "Original description"  # Should not change

    def test_update_club_with_times(self, db_session: Session, test_owner: User):
        """Test updating club with opening/closing times"""
        # Create club
        club_data = ClubCreate(
            name="Test Club",
            opening_time=time(7, 0),
            closing_time=time(22, 0),
            owner_id=test_owner.id
        )
        created_club = crud.club_crud.create_club(db_session, club_data)
        
        # Update times
        update_data = ClubUpdate(
            opening_time=time(6, 30),
            closing_time=time(23, 30)
        )
        
        updated_club = crud.club_crud.update_club(db_session, created_club, update_data)
        
        assert updated_club.opening_time == time(6, 30)
        assert updated_club.closing_time == time(23, 30)

    def test_update_club_empty_string_fields(self, db_session: Session, test_owner: User):
        """Test updating club with empty string fields"""
        # Create club
        club_data = ClubCreate(
            name="Test Club",
            description="Original description",
            owner_id=test_owner.id
        )
        created_club = crud.club_crud.create_club(db_session, club_data)
        
        # Update with empty string (should be converted to None)
        update_data = ClubUpdate(
            description="",
            amenities=""
        )
        
        updated_club = crud.club_crud.update_club(db_session, created_club, update_data)
        
        assert updated_club.description == ""  # Empty string is preserved in update
        assert updated_club.amenities == ""

    def test_update_club_all_fields(self, db_session: Session, test_owner: User):
        """Test updating all club fields"""
        # Create club
        club_data = ClubCreate(
            name="Original Club",
            owner_id=test_owner.id
        )
        created_club = crud.club_crud.create_club(db_session, club_data)
        
        # Update all fields
        update_data = ClubUpdate(
            name="Updated Club",
            description="Updated description",
            address="123 Updated St",
            city="Updated City",
            postal_code="12345",
            phone="555-0123",
            email="updated@example.com",
            opening_time=time(8, 0),
            closing_time=time(21, 0),
            amenities="Updated amenities",
            image_url="https://example.com/updated.jpg"
        )
        
        updated_club = crud.club_crud.update_club(db_session, created_club, update_data)
        
        assert updated_club.name == "Updated Club"
        assert updated_club.description == "Updated description"
        assert updated_club.address == "123 Updated St"
        assert updated_club.city == "Updated City"
        assert updated_club.postal_code == "12345"
        assert updated_club.phone == "555-0123"
        assert updated_club.email == "updated@example.com"
        assert updated_club.opening_time == time(8, 0)
        assert updated_club.closing_time == time(21, 0)
        assert updated_club.amenities == "Updated amenities"
        assert updated_club.image_url == "https://example.com/updated.jpg"

    def test_club_model_relationships(self, db_session: Session, test_owner: User):
        """Test that club model has expected relationships"""
        club_data = ClubCreate(
            name="Test Club",
            owner_id=test_owner.id
        )
        created_club = crud.club_crud.create_club(db_session, club_data)
        
        # Check that relationships exist
        assert hasattr(created_club, 'owner')
        assert hasattr(created_club, 'courts')
        assert hasattr(created_club, 'club_admins')
        
        # These should be empty initially (except owner)
        assert created_club.owner_id == test_owner.id
        assert created_club.courts == []
        assert created_club.club_admins == []

    def test_club_repr(self, db_session: Session, test_owner: User):
        """Test club string representation"""
        club_data = ClubCreate(
            name="Test Club",
            city="Test City",
            owner_id=test_owner.id
        )
        created_club = crud.club_crud.create_club(db_session, club_data)
        
        club_repr = repr(created_club)
        assert "Club(id=" in club_repr
        assert "name='Test Club'" in club_repr
        assert "city='Test City'" in club_repr

    def test_create_club_with_invalid_owner(self, db_session: Session):
        """Test club creation with invalid owner ID"""
        club_data = ClubCreate(
            name="Test Club",
            owner_id=99999  # Non-existent user
        )
        
        # This should raise an integrity error
        with pytest.raises(Exception):  # SQLAlchemy integrity error
            crud.club_crud.create_club(db_session, club_data)

    def test_get_clubs_empty_results(self, db_session: Session):
        """Test getting clubs when no clubs exist"""
        clubs = crud.club_crud.get_clubs(db_session)
        assert len(clubs) == 0

    def test_get_clubs_with_filters_no_matches(self, db_session: Session, test_owner: User):
        """Test getting clubs with filters that don't match any clubs"""
        # Create a club
        club_data = ClubCreate(
            name="Test Club",
            city="Test City",
            owner_id=test_owner.id
        )
        crud.club_crud.create_club(db_session, club_data)
        
        # Filter with non-matching criteria
        clubs = crud.club_crud.get_clubs(db_session, name="NonExistent")
        assert len(clubs) == 0
        
        clubs = crud.club_crud.get_clubs(db_session, city="NonExistent")
        assert len(clubs) == 0

    def test_get_clubs_combined_filters(self, db_session: Session, test_owner: User):
        """Test getting clubs with multiple filters combined"""
        # Create clubs
        club1_data = ClubCreate(
            name="Tennis Club Alpha",
            city="New York",
            owner_id=test_owner.id
        )
        club1 = crud.club_crud.create_club(db_session, club1_data)
        
        club2_data = ClubCreate(
            name="Tennis Club Beta",
            city="Los Angeles",
            owner_id=test_owner.id
        )
        club2 = crud.club_crud.create_club(db_session, club2_data)
        
        club3_data = ClubCreate(
            name="Padel Club Alpha",
            city="New York",
            owner_id=test_owner.id
        )
        club3 = crud.club_crud.create_club(db_session, club3_data)
        
        # Filter by both name and city
        clubs = crud.club_crud.get_clubs(db_session, name="Tennis", city="New York")
        
        assert len(clubs) == 1
        assert clubs[0].id == club1.id

    def test_club_pagination_edge_cases(self, db_session: Session, test_owner: User):
        """Test pagination edge cases"""
        # Create one club
        club_data = ClubCreate(
            name="Test Club",
            owner_id=test_owner.id
        )
        crud.club_crud.create_club(db_session, club_data)
        
        # Test with skip > total count
        clubs = crud.club_crud.get_clubs(db_session, skip=10)
        assert len(clubs) == 0
        
        # Test with limit = 0
        clubs = crud.club_crud.get_clubs(db_session, limit=0)
        assert len(clubs) == 0

    def test_club_time_validation(self, db_session: Session, test_owner: User):
        """Test club creation with various time configurations"""
        # Test with same opening and closing time
        club_data = ClubCreate(
            name="Test Club",
            opening_time=time(9, 0),
            closing_time=time(9, 0),
            owner_id=test_owner.id
        )
        created_club = crud.club_crud.create_club(db_session, club_data)
        assert created_club.opening_time == time(9, 0)
        assert created_club.closing_time == time(9, 0)
        
        # Test with closing time before opening time (24-hour operation)
        club_data2 = ClubCreate(
            name="Test Club 2",
            opening_time=time(22, 0),  # 10 PM
            closing_time=time(6, 0),   # 6 AM next day
            owner_id=test_owner.id
        )
        created_club2 = crud.club_crud.create_club(db_session, club_data2)
        assert created_club2.opening_time == time(22, 0)
        assert created_club2.closing_time == time(6, 0)

    def test_update_club_model_dump_exclude_unset(self, db_session: Session, test_owner: User):
        """Test that update uses model_dump(exclude_unset=True) correctly"""
        # Create club
        club_data = ClubCreate(
            name="Original Name",
            city="Original City",
            description="Original description",
            owner_id=test_owner.id
        )
        created_club = crud.club_crud.create_club(db_session, club_data)
        
        # Update with ClubUpdate that only sets specific fields
        update_data = ClubUpdate()
        update_data.name = "Updated Name"
        # Other fields should remain unset
        
        updated_club = crud.club_crud.update_club(db_session, created_club, update_data)
        
        assert updated_club.name == "Updated Name"
        assert updated_club.city == "Original City"  # Should not change
        assert updated_club.description == "Original description"  # Should not change