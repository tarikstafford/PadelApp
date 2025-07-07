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

    def create_bulk_tournament_bookings(
        self, db: Session, tournament_id: int, court_bookings: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Create multiple tournament court bookings at once.

        Args:
            db: Database session
            tournament_id: Tournament ID
            court_bookings: List of court booking data

        Returns:
            Dictionary containing created bookings and any failures
        """
        created_bookings = []
        failed_bookings = []

        for booking_data in court_bookings:
            try:
                # Validate court availability
                court_id = booking_data["court_id"]
                start_time = booking_data["start_time"]
                end_time = booking_data["end_time"]

                if not self.is_court_available(db, court_id, start_time, end_time):
                    failed_bookings.append(
                        {
                            "booking_data": booking_data,
                            "error": "Court is not available for the specified time slot",
                        }
                    )
                    continue

                # Create booking
                booking = TournamentCourtBooking(
                    tournament_id=tournament_id,
                    court_id=court_id,
                    start_time=start_time,
                    end_time=end_time,
                    is_occupied=False,
                )
                db.add(booking)
                db.flush()  # Get the ID without committing
                created_bookings.append(booking)

            except Exception as e:
                failed_bookings.append({"booking_data": booking_data, "error": str(e)})

        try:
            db.commit()
        except Exception as e:
            db.rollback()
            return {
                "created_bookings": [],
                "failed_bookings": court_bookings,
                "total_created": 0,
                "total_failed": len(court_bookings),
                "error": f"Database error: {e!s}",
            }

        return {
            "created_bookings": created_bookings,
            "failed_bookings": failed_bookings,
            "total_created": len(created_bookings),
            "total_failed": len(failed_bookings),
        }

    def block_courts_for_tournament(
        self,
        db: Session,
        tournament_id: int,
        time_slots: list[dict[str, Any]],
        court_ids: list[int],
    ) -> dict[str, Any]:
        """
        Block multiple courts for multiple time slots for a tournament.

        Args:
            db: Database session
            tournament_id: Tournament ID
            time_slots: List of time slot dictionaries
            court_ids: List of court IDs to block

        Returns:
            Dictionary containing blocking results
        """
        court_bookings = []

        # Generate booking data for each court and time slot combination
        for time_slot in time_slots:
            for court_id in court_ids:
                court_bookings.append(
                    {
                        "court_id": court_id,
                        "start_time": time_slot["start_time"],
                        "end_time": time_slot["end_time"],
                    }
                )

        return self.create_bulk_tournament_bookings(db, tournament_id, court_bookings)

    def release_tournament_bookings(self, db: Session, tournament_id: int) -> bool:
        """
        Release all court bookings for a tournament (when tournament is cancelled).

        Args:
            db: Database session
            tournament_id: Tournament ID

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get all court bookings for the tournament
            bookings = (
                db.query(TournamentCourtBooking)
                .filter(TournamentCourtBooking.tournament_id == tournament_id)
                .all()
            )

            # Delete all bookings
            for booking in bookings:
                db.delete(booking)

            db.commit()
            return True

        except Exception:
            db.rollback()
            return False

    def get_tournament_court_utilization(
        self, db: Session, tournament_id: int
    ) -> dict[str, Any]:
        """
        Get court utilization statistics for a tournament.

        Args:
            db: Database session
            tournament_id: Tournament ID

        Returns:
            Dictionary containing utilization statistics
        """
        bookings = (
            db.query(TournamentCourtBooking)
            .filter(TournamentCourtBooking.tournament_id == tournament_id)
            .all()
        )

        if not bookings:
            return {
                "tournament_id": tournament_id,
                "total_bookings": 0,
                "occupied_bookings": 0,
                "available_bookings": 0,
                "utilization_rate": 0.0,
                "court_breakdown": {},
            }

        total_bookings = len(bookings)
        occupied_bookings = len([b for b in bookings if b.is_occupied])
        available_bookings = total_bookings - occupied_bookings
        utilization_rate = (
            (occupied_bookings / total_bookings) * 100 if total_bookings > 0 else 0.0
        )

        # Court breakdown
        court_breakdown = {}
        for booking in bookings:
            court_id = booking.court_id
            if court_id not in court_breakdown:
                court_breakdown[court_id] = {
                    "total_slots": 0,
                    "occupied_slots": 0,
                    "available_slots": 0,
                }

            court_breakdown[court_id]["total_slots"] += 1
            if booking.is_occupied:
                court_breakdown[court_id]["occupied_slots"] += 1
            else:
                court_breakdown[court_id]["available_slots"] += 1

        return {
            "tournament_id": tournament_id,
            "total_bookings": total_bookings,
            "occupied_bookings": occupied_bookings,
            "available_bookings": available_bookings,
            "utilization_rate": utilization_rate,
            "court_breakdown": court_breakdown,
        }

    def check_courts_availability_for_tournament(
        self,
        db: Session,
        time_slots: list[dict[str, Any]],
        court_ids: list[int],
        exclude_tournament_id: Optional[int] = None,
    ) -> dict[str, Any]:
        """
        Check court availability for multiple time slots.

        Args:
            db: Database session
            time_slots: List of time slot dictionaries
            court_ids: List of court IDs to check
            exclude_tournament_id: Tournament ID to exclude from availability check

        Returns:
            Dictionary containing availability information
        """
        availability_results = {
            "available_courts": [],
            "unavailable_courts": [],
            "availability_details": {},
        }

        for court_id in court_ids:
            court_available = True
            slot_details = []

            for time_slot in time_slots:
                start_time = time_slot["start_time"]
                end_time = time_slot["end_time"]

                # Check regular bookings
                regular_booking = (
                    db.query(Booking)
                    .filter(
                        Booking.court_id == court_id,
                        Booking.status.in_(
                            [BookingStatus.CONFIRMED, BookingStatus.PENDING]
                        ),
                        Booking.start_time < end_time,
                        Booking.end_time > start_time,
                    )
                    .first()
                )

                # Check tournament bookings (excluding specified tournament)
                tournament_booking_query = db.query(TournamentCourtBooking).filter(
                    TournamentCourtBooking.court_id == court_id,
                    TournamentCourtBooking.start_time < end_time,
                    TournamentCourtBooking.end_time > start_time,
                )

                if exclude_tournament_id:
                    tournament_booking_query = tournament_booking_query.filter(
                        TournamentCourtBooking.tournament_id != exclude_tournament_id
                    )

                tournament_booking = tournament_booking_query.first()

                slot_available = not (regular_booking or tournament_booking)
                if not slot_available:
                    court_available = False

                slot_details.append(
                    {
                        "start_time": start_time.isoformat()
                        if isinstance(start_time, datetime)
                        else start_time,
                        "end_time": end_time.isoformat()
                        if isinstance(end_time, datetime)
                        else end_time,
                        "available": slot_available,
                        "blocking_type": "regular"
                        if regular_booking
                        else "tournament"
                        if tournament_booking
                        else None,
                    }
                )

            availability_results["availability_details"][court_id] = slot_details

            if court_available:
                availability_results["available_courts"].append(court_id)
            else:
                availability_results["unavailable_courts"].append(court_id)

        return availability_results


court_booking_service = CourtBookingService()
