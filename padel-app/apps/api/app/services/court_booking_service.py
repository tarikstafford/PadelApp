from datetime import datetime, timedelta
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.models.booking import Booking, BookingStatus
from app.models.court import Court
from app.models.tournament import TournamentCourtBooking


class CourtBookingService:
    """Service to handle court availability and booking conflicts with tournaments"""

    def is_court_available(
        self, db: Session, court_id: int, start_time: datetime, end_time: datetime
    ) -> bool:
        """
        Check if a court is available for booking during the specified time period.
        This includes checking for both regular bookings and tournament reservations.

        Args:
            db: Database session
            court_id: ID of the court to check
            start_time: Start time of the requested booking
            end_time: End time of the requested booking

        Returns:
            True if the court is available, False otherwise
        """
        # Check for existing regular bookings
        existing_bookings = (
            db.query(Booking)
            .filter(
                Booking.court_id == court_id,
                Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.PENDING]),
                # Check for overlap: booking starts before our end time and ends after our start time
                Booking.start_time < end_time,
                Booking.end_time > start_time,
            )
            .first()
        )

        if existing_bookings:
            return False

        # Check for tournament court bookings
        tournament_bookings = (
            db.query(TournamentCourtBooking)
            .filter(
                TournamentCourtBooking.court_id == court_id,
                TournamentCourtBooking.start_time < end_time,
                TournamentCourtBooking.end_time > start_time,
            )
            .first()
        )

        return not tournament_bookings

    def get_court_availability(
        self, db: Session, court_id: int, date: datetime
    ) -> list[dict[str, Any]]:
        """
        Get the availability slots for a court on a specific date.

        Args:
            db: Database session
            court_id: ID of the court
            date: Date to check availability for

        Returns:
            List of available time slots
        """
        court = db.query(Court).filter(Court.id == court_id).first()
        if not court:
            return []

        # Get club operating hours (default 8 AM to 10 PM)
        club = court.club
        start_hour = club.opening_time.hour if club.opening_time else 8
        end_hour = club.closing_time.hour if club.closing_time else 22

        # Generate all possible slots (assuming 1.5 hour slots)
        date_start = datetime.combine(
            date.date(), datetime.min.time().replace(hour=start_hour)
        )
        date_end = datetime.combine(
            date.date(), datetime.min.time().replace(hour=end_hour)
        )

        slots = []
        current_time = date_start
        slot_duration = timedelta(hours=1, minutes=30)  # 1.5 hours per slot

        while current_time + slot_duration <= date_end:
            slot_end = current_time + slot_duration

            if self.is_court_available(db, court_id, current_time, slot_end):
                slots.append(
                    {
                        "start_time": current_time,
                        "end_time": slot_end,
                        "available": True,
                        "type": "available",
                    }
                )
            else:
                # Check what type of booking is blocking this slot
                booking_type = self._get_blocking_booking_type(
                    db, court_id, current_time, slot_end
                )
                slots.append(
                    {
                        "start_time": current_time,
                        "end_time": slot_end,
                        "available": False,
                        "type": booking_type,
                    }
                )

            current_time += timedelta(hours=1)  # Move to next hour

        return slots

    def _get_blocking_booking_type(
        self, db: Session, court_id: int, start_time: datetime, end_time: datetime
    ) -> str:
        """
        Determine what type of booking is blocking a time slot.

        Returns:
            'booking' for regular bookings, 'tournament' for tournament bookings, 'unknown' if unclear
        """
        # Check for regular bookings first
        regular_booking = (
            db.query(Booking)
            .filter(
                Booking.court_id == court_id,
                Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.PENDING]),
                Booking.start_time < end_time,
                Booking.end_time > start_time,
            )
            .first()
        )

        if regular_booking:
            return "booking"

        # Check for tournament bookings
        tournament_booking = (
            db.query(TournamentCourtBooking)
            .filter(
                TournamentCourtBooking.court_id == court_id,
                TournamentCourtBooking.start_time < end_time,
                TournamentCourtBooking.end_time > start_time,
            )
            .first()
        )

        if tournament_booking:
            return "tournament"

        return "unknown"

    def get_tournament_blocked_times(
        self, db: Session, court_id: int, start_date: datetime, end_date: datetime
    ) -> list[dict[str, Any]]:
        """
        Get all tournament-blocked time periods for a court within a date range.

        Args:
            db: Database session
            court_id: ID of the court
            start_date: Start date to check
            end_date: End date to check

        Returns:
            List of tournament booking periods
        """
        tournament_bookings = (
            db.query(TournamentCourtBooking)
            .filter(
                TournamentCourtBooking.court_id == court_id,
                TournamentCourtBooking.start_time >= start_date,
                TournamentCourtBooking.end_time <= end_date,
            )
            .all()
        )

        return [
            {
                "start_time": booking.start_time,
                "end_time": booking.end_time,
                "tournament_id": booking.tournament_id,
                "is_occupied": booking.is_occupied,
                "match_id": booking.match_id,
            }
            for booking in tournament_bookings
        ]

    def create_booking_with_validation(
        self, db: Session, booking_data: dict[str, Any]
    ) -> Optional[Booking]:
        """
        Create a booking after validating court availability.

        Args:
            db: Database session
            booking_data: Dictionary containing booking information

        Returns:
            Created booking if successful, None if court is not available
        """
        court_id = booking_data["court_id"]
        start_time = booking_data["start_time"]
        end_time = booking_data["end_time"]

        # Validate availability
        if not self.is_court_available(db, court_id, start_time, end_time):
            return None

        # Create the booking
        booking = Booking(**booking_data)
        db.add(booking)
        db.commit()
        db.refresh(booking)

        return booking

    def update_tournament_court_usage(
        self, db: Session, match_id: int, court_booking_id: int
    ):
        """
        Mark a tournament court booking as occupied by a specific match.

        Args:
            db: Database session
            match_id: ID of the tournament match
            court_booking_id: ID of the court booking
        """
        court_booking = (
            db.query(TournamentCourtBooking)
            .filter(TournamentCourtBooking.id == court_booking_id)
            .first()
        )

        if court_booking:
            court_booking.is_occupied = True
            court_booking.match_id = match_id
            db.commit()


court_booking_service = CourtBookingService()
