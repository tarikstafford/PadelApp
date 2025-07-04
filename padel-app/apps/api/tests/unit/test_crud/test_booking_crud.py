from datetime import date, datetime, time, timedelta
from unittest.mock import Mock

from sqlalchemy.orm import Session

from app.crud.booking_crud import (
    create_booking,
    create_booking_with_game,
    get_booking,
    get_bookings_by_club,
    get_bookings_by_club_and_date,
    get_bookings_by_user,
    get_bookings_for_court_on_date,
)
from app.models.booking import Booking, BookingStatus
from app.models.court import Court
from app.models.user import User
from app.schemas.booking_schemas import BookingCreate


class TestGetBookingsForCourtOnDate:
    def test_get_bookings_for_court_on_date_found(self):
        mock_db = Mock(spec=Session)
        target_date = date(2024, 1, 15)
        court_id = 1

        mock_bookings = [
            Booking(
                id=1,
                court_id=court_id,
                start_time=datetime.combine(target_date, time(10, 0)),
                end_time=datetime.combine(target_date, time(11, 0)),
            ),
            Booking(
                id=2,
                court_id=court_id,
                start_time=datetime.combine(target_date, time(14, 0)),
                end_time=datetime.combine(target_date, time(15, 0)),
            ),
        ]

        mock_db.query.return_value.filter.return_value.all.return_value = mock_bookings

        result = get_bookings_for_court_on_date(mock_db, court_id, target_date)

        assert result == mock_bookings
        mock_db.query.assert_called_once_with(Booking)
        assert len(result) == 2

    def test_get_bookings_for_court_on_date_empty(self):
        mock_db = Mock(spec=Session)
        target_date = date(2024, 1, 15)
        court_id = 1

        mock_db.query.return_value.filter.return_value.all.return_value = []

        result = get_bookings_for_court_on_date(mock_db, court_id, target_date)

        assert result == []

    def test_get_bookings_for_court_on_date_different_courts(self):
        mock_db = Mock(spec=Session)
        target_date = date(2024, 1, 15)
        court_id = 1

        # Mock bookings only for court 1, not court 2
        mock_bookings = [
            Booking(
                id=1,
                court_id=court_id,
                start_time=datetime.combine(target_date, time(10, 0)),
                end_time=datetime.combine(target_date, time(11, 0)),
            )
        ]

        mock_db.query.return_value.filter.return_value.all.return_value = mock_bookings

        result = get_bookings_for_court_on_date(mock_db, court_id, target_date)

        assert len(result) == 1
        assert result[0].court_id == court_id


class TestCreateBooking:
    def test_create_booking_success(self):
        mock_db = Mock(spec=Session)

        booking_data = BookingCreate(
            court_id=1, start_time=datetime(2024, 1, 15, 10, 0), duration=60
        )
        user_id = 1

        # Mock the created booking
        Booking(
            id=1,
            court_id=1,
            user_id=user_id,
            start_time=booking_data.start_time,
            end_time=booking_data.start_time + timedelta(minutes=60),
            status=BookingStatus.CONFIRMED,
        )

        # Mock the final booking with relationships
        mock_final_booking = Booking(
            id=1,
            court_id=1,
            user_id=user_id,
            start_time=booking_data.start_time,
            end_time=booking_data.start_time + timedelta(minutes=60),
            status=BookingStatus.CONFIRMED,
        )
        mock_final_booking.user = User(id=user_id, email="test@example.com")
        mock_final_booking.court = Court(id=1, name="Court 1")

        # Mock database operations
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = (
            mock_final_booking
        )

        result = create_booking(mock_db, booking_data, user_id)

        # Verify database operations
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

        # Verify booking creation
        added_booking = mock_db.add.call_args[0][0]
        assert added_booking.court_id == 1
        assert added_booking.user_id == user_id
        assert added_booking.start_time == booking_data.start_time
        assert added_booking.end_time == booking_data.start_time + timedelta(minutes=60)
        assert added_booking.status == BookingStatus.CONFIRMED

        assert result == mock_final_booking

    def test_create_booking_calculates_end_time(self):
        mock_db = Mock(spec=Session)

        start_time = datetime(2024, 1, 15, 10, 0)
        duration = 90  # 1.5 hours

        booking_data = BookingCreate(
            court_id=1, start_time=start_time, duration=duration
        )

        mock_final_booking = Booking(id=1, court_id=1, user_id=1)
        mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = (
            mock_final_booking
        )

        create_booking(mock_db, booking_data, user_id=1)

        # Check that end_time was calculated correctly
        added_booking = mock_db.add.call_args[0][0]
        expected_end_time = start_time + timedelta(minutes=duration)
        assert added_booking.end_time == expected_end_time

    def test_create_booking_different_durations(self):
        mock_db = Mock(spec=Session)

        test_cases = [
            (30, timedelta(minutes=30)),
            (60, timedelta(minutes=60)),
            (120, timedelta(minutes=120)),
        ]

        for duration, expected_delta in test_cases:
            mock_db.reset_mock()

            start_time = datetime(2024, 1, 15, 10, 0)
            booking_data = BookingCreate(
                court_id=1, start_time=start_time, duration=duration
            )

            mock_final_booking = Booking(id=1, court_id=1, user_id=1)
            mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = (
                mock_final_booking
            )

            create_booking(mock_db, booking_data, user_id=1)

            added_booking = mock_db.add.call_args[0][0]
            assert added_booking.end_time == start_time + expected_delta


class TestGetBooking:
    def test_get_booking_found(self):
        mock_db = Mock(spec=Session)
        booking_id = 1

        mock_booking = Booking(
            id=booking_id,
            court_id=1,
            user_id=1,
            start_time=datetime(2024, 1, 15, 10, 0),
            end_time=datetime(2024, 1, 15, 11, 0),
        )

        mock_db.query.return_value.filter.return_value.options.return_value.first.return_value = (
            mock_booking
        )

        result = get_booking(mock_db, booking_id)

        assert result == mock_booking
        mock_db.query.assert_called_once_with(Booking)

    def test_get_booking_not_found(self):
        mock_db = Mock(spec=Session)
        booking_id = 999

        mock_db.query.return_value.filter.return_value.options.return_value.first.return_value = (
            None
        )

        result = get_booking(mock_db, booking_id)

        assert result is None

    def test_get_booking_loads_relationships(self):
        mock_db = Mock(spec=Session)
        booking_id = 1

        mock_booking = Booking(id=booking_id, court_id=1, user_id=1)
        mock_booking.court = Court(id=1, name="Court 1")
        mock_booking.user = User(id=1, email="test@example.com")

        mock_db.query.return_value.filter.return_value.options.return_value.first.return_value = (
            mock_booking
        )

        result = get_booking(mock_db, booking_id)

        # Verify options() was called for loading relationships
        mock_db.query.return_value.filter.return_value.options.assert_called_once()
        assert result == mock_booking


class TestGetBookingsByUser:
    def test_get_bookings_by_user_default_params(self):
        mock_db = Mock(spec=Session)
        user_id = 1

        mock_bookings = [
            Booking(id=1, user_id=user_id, court_id=1),
            Booking(id=2, user_id=user_id, court_id=2),
        ]

        # Mock the query chain
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = mock_bookings

        result = get_bookings_by_user(mock_db, user_id)

        assert result == mock_bookings
        mock_query.filter.assert_called()
        mock_query.offset.assert_called_with(0)
        mock_query.limit.assert_called_with(100)

    def test_get_bookings_by_user_with_pagination(self):
        mock_db = Mock(spec=Session)
        user_id = 1

        mock_bookings = [Booking(id=3, user_id=user_id, court_id=1)]

        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = mock_bookings

        result = get_bookings_by_user(mock_db, user_id, skip=10, limit=5)

        mock_query.offset.assert_called_with(10)
        mock_query.limit.assert_called_with(5)
        assert result == mock_bookings

    def test_get_bookings_by_user_with_date_filters(self):
        mock_db = Mock(spec=Session)
        user_id = 1
        start_date = date(2024, 1, 15)
        end_date = date(2024, 1, 16)

        mock_bookings = [Booking(id=1, user_id=user_id, court_id=1)]

        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = mock_bookings

        result = get_bookings_by_user(
            mock_db, user_id, start_date_filter=start_date, end_date_filter=end_date
        )

        # Verify date filters were applied
        assert mock_query.filter.call_count >= 3  # user_id + start_date + end_date
        assert result == mock_bookings

    def test_get_bookings_by_user_with_sorting(self):
        mock_db = Mock(spec=Session)
        user_id = 1

        mock_bookings = [Booking(id=1, user_id=user_id, court_id=1)]

        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = mock_bookings

        result = get_bookings_by_user(
            mock_db, user_id, sort_by="start_time", sort_desc=True
        )

        # Verify sorting was applied
        mock_query.order_by.assert_called_once()
        assert result == mock_bookings

    def test_get_bookings_by_user_empty_result(self):
        mock_db = Mock(spec=Session)
        user_id = 999

        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        result = get_bookings_by_user(mock_db, user_id)

        assert result == []


class TestGetBookingsByClub:
    def test_get_bookings_by_club_found(self):
        mock_db = Mock(spec=Session)
        club_id = 1

        mock_bookings = [
            Booking(id=1, court_id=1, user_id=1),
            Booking(id=2, court_id=2, user_id=2),
        ]

        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = mock_bookings

        result = get_bookings_by_club(mock_db, club_id)

        assert result == mock_bookings
        mock_query.filter.assert_called()

    def test_get_bookings_by_club_with_pagination(self):
        mock_db = Mock(spec=Session)
        club_id = 1

        mock_bookings = [Booking(id=1, court_id=1, user_id=1)]

        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = mock_bookings

        result = get_bookings_by_club(mock_db, club_id, skip=5, limit=10)

        mock_query.offset.assert_called_with(5)
        mock_query.limit.assert_called_with(10)
        assert result == mock_bookings


class TestGetBookingsByClubAndDate:
    def test_get_bookings_by_club_and_date_found(self):
        mock_db = Mock(spec=Session)
        club_id = 1
        target_date = date(2024, 1, 15)

        mock_bookings = [
            Booking(
                id=1,
                court_id=1,
                user_id=1,
                start_time=datetime.combine(target_date, time(10, 0)),
            ),
            Booking(
                id=2,
                court_id=2,
                user_id=2,
                start_time=datetime.combine(target_date, time(14, 0)),
            ),
        ]

        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = mock_bookings

        result = get_bookings_by_club_and_date(mock_db, club_id, target_date)

        assert result == mock_bookings
        mock_query.filter.assert_called()

    def test_get_bookings_by_club_and_date_empty(self):
        mock_db = Mock(spec=Session)
        club_id = 1
        target_date = date(2024, 1, 15)

        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        result = get_bookings_by_club_and_date(mock_db, club_id, target_date)

        assert result == []


class TestCreateBookingWithGame:
    def test_create_booking_with_game_success(self):
        mock_db = Mock(spec=Session)

        booking_data = BookingCreate(
            court_id=1, start_time=datetime(2024, 1, 15, 10, 0), duration=60
        )
        user_id = 1

        mock_booking = Booking(
            id=1,
            court_id=1,
            user_id=user_id,
            start_time=booking_data.start_time,
            end_time=booking_data.start_time + timedelta(minutes=60),
            status=BookingStatus.CONFIRMED,
        )

        mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = (
            mock_booking
        )

        create_booking_with_game(mock_db, booking_data, user_id)

        # Verify database operations
        mock_db.add.assert_called()
        mock_db.commit.assert_called()
        mock_db.refresh.assert_called()

    def test_create_booking_with_game_creates_relationships(self):
        mock_db = Mock(spec=Session)

        booking_data = BookingCreate(
            court_id=1, start_time=datetime(2024, 1, 15, 10, 0), duration=60
        )
        user_id = 1

        mock_booking_with_game = Booking(id=1, court_id=1, user_id=user_id)
        mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = (
            mock_booking_with_game
        )

        create_booking_with_game(mock_db, booking_data, user_id)

        # Should create both booking and game
        assert mock_db.add.call_count >= 2  # booking + game
        mock_db.commit.assert_called()


class TestBookingCRUDEdgeCases:
    def test_create_booking_with_zero_duration(self):
        mock_db = Mock(spec=Session)

        booking_data = BookingCreate(
            court_id=1,
            start_time=datetime(2024, 1, 15, 10, 0),
            duration=0,  # Edge case: zero duration
        )
        user_id = 1

        mock_booking = Booking(id=1, court_id=1, user_id=user_id)
        mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = (
            mock_booking
        )

        create_booking(mock_db, booking_data, user_id)

        # Should handle zero duration
        added_booking = mock_db.add.call_args[0][0]
        assert added_booking.end_time == booking_data.start_time

    def test_get_booking_with_invalid_id(self):
        mock_db = Mock(spec=Session)

        mock_db.query.return_value.filter.return_value.options.return_value.first.return_value = (
            None
        )

        result = get_booking(mock_db, booking_id=-1)

        assert result is None

    def test_get_bookings_by_user_with_future_dates(self):
        mock_db = Mock(spec=Session)
        user_id = 1

        # Test with future date filters
        future_start = date(2030, 1, 1)
        future_end = date(2030, 12, 31)

        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        result = get_bookings_by_user(
            mock_db, user_id, start_date_filter=future_start, end_date_filter=future_end
        )

        assert result == []

    def test_create_booking_with_past_time(self):
        mock_db = Mock(spec=Session)

        # Create booking with past time
        past_time = datetime(2020, 1, 15, 10, 0)
        booking_data = BookingCreate(court_id=1, start_time=past_time, duration=60)
        user_id = 1

        mock_booking = Booking(id=1, court_id=1, user_id=user_id)
        mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = (
            mock_booking
        )

        # Should still create the booking (business logic elsewhere)
        create_booking(mock_db, booking_data, user_id)

        added_booking = mock_db.add.call_args[0][0]
        assert added_booking.start_time == past_time


class TestBookingCRUDIntegration:
    def test_create_then_get_booking(self):
        """Integration test for creating and then retrieving a booking."""
        mock_db = Mock(spec=Session)

        # Create booking
        booking_data = BookingCreate(
            court_id=1, start_time=datetime(2024, 1, 15, 10, 0), duration=60
        )
        user_id = 1

        created_booking = Booking(
            id=1,
            court_id=1,
            user_id=user_id,
            start_time=booking_data.start_time,
            end_time=booking_data.start_time + timedelta(minutes=60),
            status=BookingStatus.CONFIRMED,
        )

        mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = (
            created_booking
        )

        # Create
        create_booking(mock_db, booking_data, user_id)

        # Reset mock for get operation
        mock_db.reset_mock()
        mock_db.query.return_value.filter.return_value.options.return_value.first.return_value = (
            created_booking
        )

        # Get
        result_get = get_booking(mock_db, booking_id=1)

        assert result_get.id == 1
        assert result_get.court_id == 1
        assert result_get.user_id == user_id

    def test_create_booking_with_game_workflow(self):
        """Integration test for creating a booking with game."""
        mock_db = Mock(spec=Session)

        # Create booking with game
        booking_data = BookingCreate(
            court_id=1, start_time=datetime(2024, 1, 15, 10, 0), duration=60
        )

        booking_with_game = Booking(
            id=1,
            court_id=1,
            user_id=1,
            start_time=booking_data.start_time,
            end_time=booking_data.start_time + timedelta(minutes=60),
            status=BookingStatus.CONFIRMED,
        )

        mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = (
            booking_with_game
        )

        # Create booking with game
        create_booking_with_game(mock_db, booking_data, user_id=1)

        # Verify both booking and game were created
        assert mock_db.add.call_count >= 2  # booking + game
        mock_db.commit.assert_called()

    def test_get_bookings_workflow(self):
        """Integration test for getting bookings by different criteria."""
        mock_db = Mock(spec=Session)

        # Mock data
        user_id = 1
        club_id = 1
        target_date = date(2024, 1, 15)

        mock_bookings = [
            Booking(id=1, user_id=user_id, court_id=1),
            Booking(id=2, user_id=user_id, court_id=2),
        ]

        # Setup mock query chains for different methods
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = mock_bookings

        # Test getting bookings by user
        user_bookings = get_bookings_by_user(mock_db, user_id)
        assert user_bookings == mock_bookings

        # Test getting bookings by club
        mock_db.reset_mock()
        mock_db.query.return_value = mock_query
        club_bookings = get_bookings_by_club(mock_db, club_id)
        assert club_bookings == mock_bookings

        # Test getting bookings by club and date
        mock_db.reset_mock()
        mock_db.query.return_value = mock_query
        date_bookings = get_bookings_by_club_and_date(mock_db, club_id, target_date)
        assert date_bookings == mock_bookings
