import datetime
from unittest.mock import Mock, patch

import pytest
from sqlalchemy.orm import Session

from app.schemas.court_schemas import (
    AvailabilityResponse,
    BookingTimeSlot,
    CalendarTimeSlot,
    DailyAvailability,
)
from app.services.availability_service import (
    DEFAULT_CLOSING_TIME,
    DEFAULT_OPENING_TIME,
    get_court_availability_for_day,
    get_court_availability_for_range,
)


class TestAvailabilityService:
    """Test suite for availability service functions"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_db = Mock(spec=Session)
        self.court_id = 1
        self.target_date = datetime.date(2024, 1, 15)
        self.duration = 90

        # Mock court with club
        self.mock_court = Mock()
        self.mock_club = Mock()
        self.mock_club.opening_time = datetime.time(9, 0)
        self.mock_club.closing_time = datetime.time(22, 0)
        self.mock_court.club = self.mock_club

        # Mock booking
        self.mock_booking = Mock()
        self.mock_booking.start_time = datetime.datetime(2024, 1, 15, 10, 0)

    @patch("app.services.availability_service.crud.court_crud.get_court")
    @patch(
        "app.services.availability_service.crud.booking_crud.get_bookings_for_court_on_date"
    )
    @patch("app.services.availability_service.get_time_slots")
    def test_get_court_availability_for_day_success(
        self, mock_get_time_slots, mock_get_bookings, mock_get_court
    ):
        """Test successful court availability retrieval for a single day"""
        # Setup mocks
        mock_get_court.return_value = self.mock_court
        mock_get_bookings.return_value = [self.mock_booking]
        mock_get_time_slots.return_value = [
            (datetime.time(9, 0), datetime.time(10, 30)),
            (datetime.time(10, 30), datetime.time(12, 0)),
            (datetime.time(12, 0), datetime.time(13, 30)),
        ]

        # Execute
        result = get_court_availability_for_day(
            self.mock_db,
            court_id=self.court_id,
            target_date=self.target_date,
            duration=self.duration,
        )

        # Verify
        assert isinstance(result, list)
        assert len(result) == 3
        assert all(isinstance(slot, BookingTimeSlot) for slot in result)

        # Verify mock calls
        mock_get_court.assert_called_once_with(self.mock_db, court_id=self.court_id)
        mock_get_bookings.assert_called_once_with(
            self.mock_db, court_id=self.court_id, target_date=self.target_date
        )
        mock_get_time_slots.assert_called_once_with(
            self.mock_club.opening_time, self.mock_club.closing_time, self.duration
        )

    @patch("app.services.availability_service.crud.court_crud.get_court")
    def test_get_court_availability_for_day_court_not_found(self, mock_get_court):
        """Test court availability when court is not found"""
        # Setup
        mock_get_court.return_value = None

        # Execute
        result = get_court_availability_for_day(
            self.mock_db, court_id=self.court_id, target_date=self.target_date
        )

        # Verify
        assert result == []
        mock_get_court.assert_called_once_with(self.mock_db, court_id=self.court_id)

    @patch("app.services.availability_service.crud.court_crud.get_court")
    @patch(
        "app.services.availability_service.crud.booking_crud.get_bookings_for_court_on_date"
    )
    @patch("app.services.availability_service.get_time_slots")
    def test_get_court_availability_for_day_with_default_times(
        self, mock_get_time_slots, mock_get_bookings, mock_get_court
    ):
        """Test court availability with default opening/closing times"""
        # Setup - club with no opening/closing times
        mock_club_no_times = Mock()
        mock_club_no_times.opening_time = None
        mock_club_no_times.closing_time = None
        mock_court_no_times = Mock()
        mock_court_no_times.club = mock_club_no_times

        mock_get_court.return_value = mock_court_no_times
        mock_get_bookings.return_value = []
        mock_get_time_slots.return_value = [
            (datetime.time(9, 0), datetime.time(10, 30))
        ]

        # Execute
        result = get_court_availability_for_day(
            self.mock_db, court_id=self.court_id, target_date=self.target_date
        )

        # Verify
        assert isinstance(result, list)
        mock_get_time_slots.assert_called_once_with(
            DEFAULT_OPENING_TIME, DEFAULT_CLOSING_TIME, self.duration
        )

    @patch("app.services.availability_service.crud.court_crud.get_court")
    @patch(
        "app.services.availability_service.crud.booking_crud.get_bookings_for_court_on_date"
    )
    @patch("app.services.availability_service.get_time_slots")
    @patch("app.services.availability_service.datetime")
    def test_get_court_availability_for_day_past_slots_unavailable(
        self, mock_datetime, mock_get_time_slots, mock_get_bookings, mock_get_court
    ):
        """Test that past time slots are marked as unavailable"""
        # Setup - current time is 11:00 AM
        mock_now = datetime.datetime(2024, 1, 15, 11, 0)
        mock_datetime.datetime.now.return_value = mock_now
        mock_datetime.datetime.combine = datetime.datetime.combine

        mock_get_court.return_value = self.mock_court
        mock_get_bookings.return_value = []
        mock_get_time_slots.return_value = [
            (datetime.time(9, 0), datetime.time(10, 30)),  # Past
            (datetime.time(10, 30), datetime.time(12, 0)),  # Current/Future
            (datetime.time(12, 0), datetime.time(13, 30)),  # Future
        ]

        # Execute
        result = get_court_availability_for_day(
            self.mock_db, court_id=self.court_id, target_date=self.target_date
        )

        # Verify
        assert len(result) == 3
        assert not result[0].is_available  # Past slot
        assert result[1].is_available  # Current/Future slot
        assert result[2].is_available  # Future slot

    @patch("app.services.availability_service.crud.court_crud.get_court")
    @patch(
        "app.services.availability_service.crud.booking_crud.get_bookings_for_court_on_date"
    )
    @patch("app.services.availability_service.get_time_slots")
    def test_get_court_availability_for_day_booked_slots_unavailable(
        self, mock_get_time_slots, mock_get_bookings, mock_get_court
    ):
        """Test that booked time slots are marked as unavailable"""
        # Setup - booking at 10:30 AM
        mock_booking_1030 = Mock()
        mock_booking_1030.start_time = datetime.datetime(2024, 1, 15, 10, 30)

        mock_get_court.return_value = self.mock_court
        mock_get_bookings.return_value = [mock_booking_1030]
        mock_get_time_slots.return_value = [
            (datetime.time(9, 0), datetime.time(10, 30)),
            (datetime.time(10, 30), datetime.time(12, 0)),  # Booked
            (datetime.time(12, 0), datetime.time(13, 30)),
        ]

        # Execute
        result = get_court_availability_for_day(
            self.mock_db, court_id=self.court_id, target_date=self.target_date
        )

        # Verify
        assert len(result) == 3
        assert not result[1].is_available  # Booked slot

    @patch("app.services.availability_service.crud.court_crud.get_court")
    @patch(
        "app.services.availability_service.crud.booking_crud.get_bookings_for_court_on_date"
    )
    @patch("app.services.availability_service.get_time_slots")
    def test_get_court_availability_for_day_slot_format(
        self, mock_get_time_slots, mock_get_bookings, mock_get_court
    ):
        """Test that time slots are formatted correctly"""
        # Setup
        mock_get_court.return_value = self.mock_court
        mock_get_bookings.return_value = []
        mock_get_time_slots.return_value = [
            (datetime.time(9, 0), datetime.time(10, 30))
        ]

        # Execute
        result = get_court_availability_for_day(
            self.mock_db, court_id=self.court_id, target_date=self.target_date
        )

        # Verify
        assert len(result) == 1
        slot = result[0]
        assert slot.start_time == "2024-01-15T09:00:00"
        assert slot.end_time == "2024-01-15T10:30:00"

    @patch("app.services.availability_service.crud.court_crud.get_court")
    @patch(
        "app.services.availability_service.crud.booking_crud.get_bookings_for_court_on_date"
    )
    @patch("app.services.availability_service.get_time_slots")
    async def test_get_court_availability_for_range_success(
        self, mock_get_time_slots, mock_get_bookings, mock_get_court
    ):
        """Test successful court availability retrieval for date range"""
        # Setup
        start_date = datetime.date(2024, 1, 15)
        end_date = datetime.date(2024, 1, 16)

        mock_get_court.return_value = self.mock_court
        mock_get_bookings.return_value = []
        mock_get_time_slots.return_value = [
            (datetime.time(9, 0), datetime.time(10, 30)),
            (datetime.time(10, 30), datetime.time(12, 0)),
        ]

        # Execute
        result = await get_court_availability_for_range(
            self.mock_db,
            court_id=self.court_id,
            start_date=start_date,
            end_date=end_date,
        )

        # Verify
        assert isinstance(result, AvailabilityResponse)
        assert len(result.days) == 2  # Two days

        # Verify each day
        for day in result.days:
            assert isinstance(day, DailyAvailability)
            assert len(day.slots) == 2  # Two slots per day
            for slot in day.slots:
                assert isinstance(slot, CalendarTimeSlot)

    @patch("app.services.availability_service.crud.court_crud.get_court")
    async def test_get_court_availability_for_range_court_not_found(
        self, mock_get_court
    ):
        """Test court availability range when court is not found"""
        # Setup
        mock_get_court.return_value = None
        start_date = datetime.date(2024, 1, 15)
        end_date = datetime.date(2024, 1, 16)

        # Execute
        result = await get_court_availability_for_range(
            self.mock_db,
            court_id=self.court_id,
            start_date=start_date,
            end_date=end_date,
        )

        # Verify
        assert isinstance(result, AvailabilityResponse)
        assert result.days == []

    @patch("app.services.availability_service.crud.court_crud.get_court")
    @patch(
        "app.services.availability_service.crud.booking_crud.get_bookings_for_court_on_date"
    )
    @patch("app.services.availability_service.get_time_slots")
    async def test_get_court_availability_for_range_with_bookings(
        self, mock_get_time_slots, mock_get_bookings, mock_get_court
    ):
        """Test court availability range with existing bookings"""
        # Setup
        start_date = datetime.date(2024, 1, 15)
        end_date = datetime.date(2024, 1, 15)  # Single day

        mock_booking = Mock()
        mock_booking.start_time = datetime.datetime(2024, 1, 15, 9, 0)

        mock_get_court.return_value = self.mock_court
        mock_get_bookings.return_value = [mock_booking]
        mock_get_time_slots.return_value = [
            (datetime.time(9, 0), datetime.time(10, 30)),
            (datetime.time(10, 30), datetime.time(12, 0)),
        ]

        # Execute
        result = await get_court_availability_for_range(
            self.mock_db,
            court_id=self.court_id,
            start_date=start_date,
            end_date=end_date,
        )

        # Verify
        assert len(result.days) == 1
        day = result.days[0]
        assert len(day.slots) == 2
        assert day.slots[0].booked  # First slot is booked
        assert not day.slots[1].booked  # Second slot is available

    @patch("app.services.availability_service.crud.court_crud.get_court")
    @patch(
        "app.services.availability_service.crud.booking_crud.get_bookings_for_court_on_date"
    )
    @patch("app.services.availability_service.get_time_slots")
    async def test_get_court_availability_for_range_multiple_days(
        self, mock_get_time_slots, mock_get_bookings, mock_get_court
    ):
        """Test court availability for multiple days"""
        # Setup
        start_date = datetime.date(2024, 1, 15)
        end_date = datetime.date(2024, 1, 17)  # 3 days

        mock_get_court.return_value = self.mock_court
        mock_get_bookings.return_value = []
        mock_get_time_slots.return_value = [
            (datetime.time(9, 0), datetime.time(10, 30))
        ]

        # Execute
        result = await get_court_availability_for_range(
            self.mock_db,
            court_id=self.court_id,
            start_date=start_date,
            end_date=end_date,
        )

        # Verify
        assert len(result.days) == 3
        expected_dates = [
            datetime.date(2024, 1, 15),
            datetime.date(2024, 1, 16),
            datetime.date(2024, 1, 17),
        ]

        for i, day in enumerate(result.days):
            assert day.date == expected_dates[i]
            assert len(day.slots) == 1

    @patch("app.services.availability_service.crud.court_crud.get_court")
    @patch(
        "app.services.availability_service.crud.booking_crud.get_bookings_for_court_on_date"
    )
    @patch("app.services.availability_service.get_time_slots")
    async def test_get_court_availability_for_range_time_slot_format(
        self, mock_get_time_slots, mock_get_bookings, mock_get_court
    ):
        """Test time slot format in range availability"""
        # Setup
        start_date = datetime.date(2024, 1, 15)
        end_date = datetime.date(2024, 1, 15)

        mock_get_court.return_value = self.mock_court
        mock_get_bookings.return_value = []
        mock_get_time_slots.return_value = [
            (datetime.time(9, 0), datetime.time(10, 30)),
            (datetime.time(14, 30), datetime.time(16, 0)),
        ]

        # Execute
        result = await get_court_availability_for_range(
            self.mock_db,
            court_id=self.court_id,
            start_date=start_date,
            end_date=end_date,
        )

        # Verify
        day = result.days[0]
        assert day.slots[0].time == "09:00"
        assert day.slots[1].time == "14:30"

    @patch("app.services.availability_service.crud.court_crud.get_court")
    @patch(
        "app.services.availability_service.crud.booking_crud.get_bookings_for_court_on_date"
    )
    @patch("app.services.availability_service.get_time_slots")
    async def test_get_court_availability_for_range_with_default_times(
        self, mock_get_time_slots, mock_get_bookings, mock_get_court
    ):
        """Test court availability range with default opening/closing times"""
        # Setup
        mock_club_no_times = Mock()
        mock_club_no_times.opening_time = None
        mock_club_no_times.closing_time = None
        mock_court_no_times = Mock()
        mock_court_no_times.club = mock_club_no_times

        start_date = datetime.date(2024, 1, 15)
        end_date = datetime.date(2024, 1, 15)

        mock_get_court.return_value = mock_court_no_times
        mock_get_bookings.return_value = []
        mock_get_time_slots.return_value = [
            (datetime.time(9, 0), datetime.time(10, 30))
        ]

        # Execute
        result = await get_court_availability_for_range(
            self.mock_db,
            court_id=self.court_id,
            start_date=start_date,
            end_date=end_date,
        )

        # Verify
        assert len(result.days) == 1
        mock_get_time_slots.assert_called_with(
            DEFAULT_OPENING_TIME, DEFAULT_CLOSING_TIME, 90
        )

    def test_edge_case_same_start_end_date(self):
        """Test edge case where start_date equals end_date"""
        with patch(
            "app.services.availability_service.crud.court_crud.get_court"
        ) as mock_get_court:
            mock_get_court.return_value = self.mock_court

            with patch(
                "app.services.availability_service.crud.booking_crud.get_bookings_for_court_on_date"
            ) as mock_get_bookings:
                mock_get_bookings.return_value = []

                with patch(
                    "app.services.availability_service.get_time_slots"
                ) as mock_get_time_slots:
                    mock_get_time_slots.return_value = []

                    # Execute
                    async def test_execution():
                        return await get_court_availability_for_range(
                            self.mock_db,
                            court_id=self.court_id,
                            start_date=self.target_date,
                            end_date=self.target_date,
                        )

                    import asyncio

                    result = asyncio.run(test_execution())

                    # Verify
                    assert len(result.days) == 1
                    assert result.days[0].date == self.target_date

    def test_invalid_duration_parameter(self):
        """Test behavior with invalid duration parameter"""
        with patch(
            "app.services.availability_service.crud.court_crud.get_court"
        ) as mock_get_court:
            mock_get_court.return_value = self.mock_court

            with patch(
                "app.services.availability_service.crud.booking_crud.get_bookings_for_court_on_date"
            ) as mock_get_bookings:
                mock_get_bookings.return_value = []

                with patch(
                    "app.services.availability_service.get_time_slots"
                ) as mock_get_time_slots:
                    mock_get_time_slots.return_value = []

                    # Execute with zero duration
                    result = get_court_availability_for_day(
                        self.mock_db,
                        court_id=self.court_id,
                        target_date=self.target_date,
                        duration=0,
                    )

                    # Verify
                    assert isinstance(result, list)
                    mock_get_time_slots.assert_called_once_with(
                        self.mock_club.opening_time, self.mock_club.closing_time, 0
                    )

    def test_error_handling_db_exception(self):
        """Test error handling when database operations fail"""
        with patch(
            "app.services.availability_service.crud.court_crud.get_court"
        ) as mock_get_court:
            mock_get_court.side_effect = Exception("Database error")

            # Execute and verify exception is raised
            with pytest.raises(Exception, match="Database error"):
                get_court_availability_for_day(
                    self.mock_db, court_id=self.court_id, target_date=self.target_date
                )
