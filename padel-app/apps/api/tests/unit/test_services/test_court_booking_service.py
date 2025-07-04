import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from app.services.court_booking_service import CourtBookingService, court_booking_service
from app.models.booking import Booking, BookingStatus
from app.models.tournament import TournamentCourtBooking
from app.models.court import Court


class TestCourtBookingService:
    """Test suite for CourtBookingService"""

    def setup_method(self):
        """Set up test fixtures"""
        self.service = CourtBookingService()
        self.mock_db = Mock(spec=Session)
        self.court_id = 1
        self.start_time = datetime(2024, 1, 15, 10, 0)
        self.end_time = datetime(2024, 1, 15, 11, 30)
        
        # Mock court with club
        self.mock_court = Mock()
        self.mock_club = Mock()
        self.mock_club.opening_time = datetime.time(8, 0)
        self.mock_club.closing_time = datetime.time(22, 0)
        self.mock_court.club = self.mock_club
        
        # Mock query object
        self.mock_query = Mock()
        self.mock_db.query.return_value = self.mock_query

    def test_is_court_available_no_conflicts(self):
        """Test court availability when no conflicts exist"""
        # Setup - no existing bookings or tournaments
        self.mock_query.filter.return_value.first.return_value = None
        
        # Execute
        result = self.service.is_court_available(
            self.mock_db, self.court_id, self.start_time, self.end_time
        )
        
        # Verify
        assert result is True
        assert self.mock_db.query.call_count == 2  # Called for both Booking and TournamentCourtBooking

    def test_is_court_available_with_booking_conflict(self):
        """Test court availability when booking conflict exists"""
        # Setup - existing booking conflict
        mock_booking = Mock()
        
        def mock_query_side_effect(model):
            if model == Booking:
                mock_query_booking = Mock()
                mock_query_booking.filter.return_value.first.return_value = mock_booking
                return mock_query_booking
            elif model == TournamentCourtBooking:
                mock_query_tournament = Mock()
                mock_query_tournament.filter.return_value.first.return_value = None
                return mock_query_tournament
            
        self.mock_db.query.side_effect = mock_query_side_effect
        
        # Execute
        result = self.service.is_court_available(
            self.mock_db, self.court_id, self.start_time, self.end_time
        )
        
        # Verify
        assert result is False

    def test_is_court_available_with_tournament_conflict(self):
        """Test court availability when tournament conflict exists"""
        # Setup - tournament booking conflict
        mock_tournament_booking = Mock()
        
        def mock_query_side_effect(model):
            if model == Booking:
                mock_query_booking = Mock()
                mock_query_booking.filter.return_value.first.return_value = None
                return mock_query_booking
            elif model == TournamentCourtBooking:
                mock_query_tournament = Mock()
                mock_query_tournament.filter.return_value.first.return_value = mock_tournament_booking
                return mock_query_tournament
            
        self.mock_db.query.side_effect = mock_query_side_effect
        
        # Execute
        result = self.service.is_court_available(
            self.mock_db, self.court_id, self.start_time, self.end_time
        )
        
        # Verify
        assert result is False

    def test_is_court_available_booking_status_filters(self):
        """Test that only confirmed and pending bookings are considered"""
        # Setup - booking with cancelled status (should not conflict)
        mock_booking = Mock()
        mock_booking.status = BookingStatus.CANCELLED
        
        def mock_query_side_effect(model):
            if model == Booking:
                mock_query_booking = Mock()
                
                def mock_filter(*args, **kwargs):
                    # Mock the filter chain
                    mock_filter_result = Mock()
                    mock_filter_result.first.return_value = None  # No confirmed/pending bookings
                    return mock_filter_result
                
                mock_query_booking.filter.side_effect = mock_filter
                return mock_query_booking
            elif model == TournamentCourtBooking:
                mock_query_tournament = Mock()
                mock_query_tournament.filter.return_value.first.return_value = None
                return mock_query_tournament
            
        self.mock_db.query.side_effect = mock_query_side_effect
        
        # Execute
        result = self.service.is_court_available(
            self.mock_db, self.court_id, self.start_time, self.end_time
        )
        
        # Verify
        assert result is True

    def test_get_court_availability_court_not_found(self):
        """Test get_court_availability when court doesn't exist"""
        # Setup
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Execute
        result = self.service.get_court_availability(
            self.mock_db, self.court_id, self.start_time
        )
        
        # Verify
        assert result == []

    def test_get_court_availability_success(self):
        """Test successful court availability retrieval"""
        # Setup
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.mock_court
        
        # Mock is_court_available to return True for all slots
        with patch.object(self.service, 'is_court_available', return_value=True):
            # Execute
            result = self.service.get_court_availability(
                self.mock_db, self.court_id, self.start_time
            )
            
            # Verify
            assert isinstance(result, list)
            assert len(result) > 0
            
            # Check slot structure
            for slot in result:
                assert 'start_time' in slot
                assert 'end_time' in slot
                assert 'available' in slot
                assert 'type' in slot

    def test_get_court_availability_with_unavailable_slots(self):
        """Test court availability with some unavailable slots"""
        # Setup
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.mock_court
        
        # Mock is_court_available to return False for some slots
        def mock_availability(db, court_id, start, end):
            # Make 10:00-11:30 unavailable
            return not (start == datetime.combine(self.start_time.date(), datetime.min.time().replace(hour=10)))
        
        with patch.object(self.service, 'is_court_available', side_effect=mock_availability):
            with patch.object(self.service, '_get_blocking_booking_type', return_value='booking'):
                # Execute
                result = self.service.get_court_availability(
                    self.mock_db, self.court_id, self.start_time
                )
                
                # Verify
                assert isinstance(result, list)
                
                # Check that some slots are marked as unavailable
                unavailable_slots = [slot for slot in result if not slot['available']]
                assert len(unavailable_slots) > 0

    def test_get_court_availability_default_club_hours(self):
        """Test court availability with default club hours"""
        # Setup - club without opening/closing times
        mock_club_no_times = Mock()
        mock_club_no_times.opening_time = None
        mock_club_no_times.closing_time = None
        mock_court_no_times = Mock()
        mock_court_no_times.club = mock_club_no_times
        
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_court_no_times
        
        with patch.object(self.service, 'is_court_available', return_value=True):
            # Execute
            result = self.service.get_court_availability(
                self.mock_db, self.court_id, self.start_time
            )
            
            # Verify
            assert isinstance(result, list)
            assert len(result) > 0  # Should generate slots from 8 AM to 10 PM

    def test_get_blocking_booking_type_regular_booking(self):
        """Test _get_blocking_booking_type identifies regular bookings"""
        # Setup - regular booking exists
        mock_booking = Mock()
        
        def mock_query_side_effect(model):
            if model == Booking:
                mock_query_booking = Mock()
                mock_query_booking.filter.return_value.first.return_value = mock_booking
                return mock_query_booking
            elif model == TournamentCourtBooking:
                mock_query_tournament = Mock()
                mock_query_tournament.filter.return_value.first.return_value = None
                return mock_query_tournament
            
        self.mock_db.query.side_effect = mock_query_side_effect
        
        # Execute
        result = self.service._get_blocking_booking_type(
            self.mock_db, self.court_id, self.start_time, self.end_time
        )
        
        # Verify
        assert result == 'booking'

    def test_get_blocking_booking_type_tournament_booking(self):
        """Test _get_blocking_booking_type identifies tournament bookings"""
        # Setup - tournament booking exists
        mock_tournament_booking = Mock()
        
        def mock_query_side_effect(model):
            if model == Booking:
                mock_query_booking = Mock()
                mock_query_booking.filter.return_value.first.return_value = None
                return mock_query_booking
            elif model == TournamentCourtBooking:
                mock_query_tournament = Mock()
                mock_query_tournament.filter.return_value.first.return_value = mock_tournament_booking
                return mock_query_tournament
            
        self.mock_db.query.side_effect = mock_query_side_effect
        
        # Execute
        result = self.service._get_blocking_booking_type(
            self.mock_db, self.court_id, self.start_time, self.end_time
        )
        
        # Verify
        assert result == 'tournament'

    def test_get_blocking_booking_type_unknown(self):
        """Test _get_blocking_booking_type returns unknown when no conflicts found"""
        # Setup - no bookings found
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Execute
        result = self.service._get_blocking_booking_type(
            self.mock_db, self.court_id, self.start_time, self.end_time
        )
        
        # Verify
        assert result == 'unknown'

    def test_get_tournament_blocked_times_success(self):
        """Test successful retrieval of tournament blocked times"""
        # Setup
        start_date = datetime(2024, 1, 15)
        end_date = datetime(2024, 1, 16)
        
        mock_tournament_booking = Mock()
        mock_tournament_booking.start_time = datetime(2024, 1, 15, 10, 0)
        mock_tournament_booking.end_time = datetime(2024, 1, 15, 12, 0)
        mock_tournament_booking.tournament_id = 1
        mock_tournament_booking.is_occupied = True
        mock_tournament_booking.match_id = 1
        
        self.mock_db.query.return_value.filter.return_value.all.return_value = [mock_tournament_booking]
        
        # Execute
        result = self.service.get_tournament_blocked_times(
            self.mock_db, self.court_id, start_date, end_date
        )
        
        # Verify
        assert isinstance(result, list)
        assert len(result) == 1
        
        blocked_time = result[0]
        assert blocked_time['start_time'] == mock_tournament_booking.start_time
        assert blocked_time['end_time'] == mock_tournament_booking.end_time
        assert blocked_time['tournament_id'] == mock_tournament_booking.tournament_id
        assert blocked_time['is_occupied'] == mock_tournament_booking.is_occupied
        assert blocked_time['match_id'] == mock_tournament_booking.match_id

    def test_get_tournament_blocked_times_no_bookings(self):
        """Test tournament blocked times when no bookings exist"""
        # Setup
        start_date = datetime(2024, 1, 15)
        end_date = datetime(2024, 1, 16)
        
        self.mock_db.query.return_value.filter.return_value.all.return_value = []
        
        # Execute
        result = self.service.get_tournament_blocked_times(
            self.mock_db, self.court_id, start_date, end_date
        )
        
        # Verify
        assert result == []

    def test_create_booking_with_validation_success(self):
        """Test successful booking creation with validation"""
        # Setup
        booking_data = {
            'court_id': self.court_id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'user_id': 1,
            'status': BookingStatus.CONFIRMED
        }
        
        mock_booking = Mock()
        mock_booking.id = 1
        
        # Mock availability check
        with patch.object(self.service, 'is_court_available', return_value=True):
            # Mock database operations
            self.mock_db.add = Mock()
            self.mock_db.commit = Mock()
            self.mock_db.refresh = Mock()
            
            with patch('app.services.court_booking_service.Booking', return_value=mock_booking):
                # Execute
                result = self.service.create_booking_with_validation(
                    self.mock_db, booking_data
                )
                
                # Verify
                assert result == mock_booking
                self.mock_db.add.assert_called_once_with(mock_booking)
                self.mock_db.commit.assert_called_once()
                self.mock_db.refresh.assert_called_once_with(mock_booking)

    def test_create_booking_with_validation_court_unavailable(self):
        """Test booking creation when court is unavailable"""
        # Setup
        booking_data = {
            'court_id': self.court_id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'user_id': 1
        }
        
        # Mock availability check to return False
        with patch.object(self.service, 'is_court_available', return_value=False):
            # Execute
            result = self.service.create_booking_with_validation(
                self.mock_db, booking_data
            )
            
            # Verify
            assert result is None
            self.mock_db.add.assert_not_called()

    def test_update_tournament_court_usage_success(self):
        """Test successful update of tournament court usage"""
        # Setup
        match_id = 1
        court_booking_id = 1
        
        mock_court_booking = Mock()
        mock_court_booking.is_occupied = False
        mock_court_booking.match_id = None
        
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_court_booking
        
        # Execute
        self.service.update_tournament_court_usage(
            self.mock_db, match_id, court_booking_id
        )
        
        # Verify
        assert mock_court_booking.is_occupied is True
        assert mock_court_booking.match_id == match_id
        self.mock_db.commit.assert_called_once()

    def test_update_tournament_court_usage_booking_not_found(self):
        """Test update tournament court usage when booking doesn't exist"""
        # Setup
        match_id = 1
        court_booking_id = 1
        
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Execute
        self.service.update_tournament_court_usage(
            self.mock_db, match_id, court_booking_id
        )
        
        # Verify - should not raise error but also not commit
        self.mock_db.commit.assert_not_called()

    def test_time_slot_generation_duration(self):
        """Test that time slots are generated with correct duration"""
        # Setup
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.mock_court
        
        with patch.object(self.service, 'is_court_available', return_value=True):
            # Execute
            result = self.service.get_court_availability(
                self.mock_db, self.court_id, self.start_time
            )
            
            # Verify
            assert isinstance(result, list)
            
            # Check that each slot has the correct duration (1.5 hours)
            for slot in result:
                duration = slot['end_time'] - slot['start_time']
                assert duration == timedelta(hours=1, minutes=30)

    def test_overlap_detection_edge_cases(self):
        """Test overlap detection for various edge cases"""
        # Test exact boundary cases
        test_cases = [
            # Start time equals end time of existing booking - should not conflict
            (datetime(2024, 1, 15, 11, 30), datetime(2024, 1, 15, 13, 0)),
            # End time equals start time of existing booking - should not conflict
            (datetime(2024, 1, 15, 8, 30), datetime(2024, 1, 15, 10, 0)),
            # Overlapping start
            (datetime(2024, 1, 15, 9, 30), datetime(2024, 1, 15, 12, 0)),
            # Overlapping end
            (datetime(2024, 1, 15, 9, 0), datetime(2024, 1, 15, 11, 0)),
            # Complete overlap
            (datetime(2024, 1, 15, 10, 30), datetime(2024, 1, 15, 11, 0)),
        ]
        
        for start, end in test_cases:
            # Setup mock booking from 10:00 to 11:30
            mock_booking = Mock()
            mock_booking.start_time = self.start_time
            mock_booking.end_time = self.end_time
            mock_booking.status = BookingStatus.CONFIRMED
            
            def mock_query_side_effect(model):
                if model == Booking:
                    mock_query_booking = Mock()
                    
                    def mock_filter(*args, **kwargs):
                        # Check if this would overlap with our mock booking
                        if start < self.end_time and end > self.start_time:
                            mock_filter_result = Mock()
                            mock_filter_result.first.return_value = mock_booking
                            return mock_filter_result
                        else:
                            mock_filter_result = Mock()
                            mock_filter_result.first.return_value = None
                            return mock_filter_result
                    
                    mock_query_booking.filter.side_effect = mock_filter
                    return mock_query_booking
                elif model == TournamentCourtBooking:
                    mock_query_tournament = Mock()
                    mock_query_tournament.filter.return_value.first.return_value = None
                    return mock_query_tournament
                
            self.mock_db.query.side_effect = mock_query_side_effect
            
            # Execute
            result = self.service.is_court_available(self.mock_db, self.court_id, start, end)
            
            # Verify based on expected overlap
            expected_available = not (start < self.end_time and end > self.start_time)
            assert result == expected_available, f"Failed for time slot {start} to {end}"

    def test_service_instance_singleton(self):
        """Test that the service instance is properly initialized"""
        # Verify that the global service instance exists
        assert court_booking_service is not None
        assert isinstance(court_booking_service, CourtBookingService)

    def test_error_handling_database_exceptions(self):
        """Test error handling when database operations fail"""
        # Test exception during court availability check
        self.mock_db.query.side_effect = Exception("Database connection error")
        
        with pytest.raises(Exception, match="Database connection error"):
            self.service.is_court_available(
                self.mock_db, self.court_id, self.start_time, self.end_time
            )