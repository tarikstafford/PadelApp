from datetime import datetime, timedelta
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.crud.tournament_crud import tournament_crud
from app.models.tournament import (
    TournamentCategory,
    TournamentCourtBooking,
    TournamentType,
)
from app.services.court_booking_service import court_booking_service


class TournamentScheduleService:
    """Service for automatically scheduling tournaments with hourly time slots and court management"""

    def __init__(self):
        self.slot_duration = timedelta(hours=1)  # Hourly slots
        self.match_duration = timedelta(hours=1, minutes=30)  # 1.5 hours per match
        self.break_duration = timedelta(minutes=15)  # 15 minutes between matches

    def calculate_tournament_schedule(
        self,
        db: Session,
        tournament_id: int,
        selected_time_slots: list[dict[str, Any]],
        court_ids: list[int],
    ) -> Optional[dict[str, Any]]:
        """
        Calculate the optimal tournament schedule based on selected time slots and available courts.

        Args:
            db: Database session
            tournament_id: Tournament ID
            selected_time_slots: List of selected hourly time slots
            court_ids: List of available court IDs

        Returns:
            Dictionary containing the calculated schedule or None if scheduling fails
        """
        tournament = tournament_crud.get_tournament(db, tournament_id)
        if not tournament:
            return None

        # Get tournament teams per category
        teams_by_category = {}
        for category_config in tournament.categories:
            teams = tournament_crud.get_tournament_teams(
                db, tournament_id, category_config.category
            )
            teams_by_category[category_config.category] = teams

        # Calculate matches needed per category
        matches_by_category = {}
        for category, teams in teams_by_category.items():
            matches_needed = self._calculate_matches_needed(
                tournament.tournament_type, len(teams)
            )
            matches_by_category[category] = matches_needed

        # Convert time slots to datetime objects
        time_slots = self._parse_time_slots(selected_time_slots)

        # Validate court availability
        available_courts = self._validate_court_availability(db, court_ids, time_slots)
        if not available_courts:
            return None

        # Generate schedule
        schedule = self._generate_schedule(
            tournament.tournament_type,
            matches_by_category,
            time_slots,
            available_courts,
        )

        return {
            "tournament_id": tournament_id,
            "schedule": schedule,
            "total_matches": sum(matches_by_category.values()),
            "total_time_slots": len(time_slots),
            "courts_required": len(available_courts),
            "estimated_duration": self._calculate_estimated_duration(schedule),
        }

    def create_tournament_court_bookings(
        self,
        db: Session,
        tournament_id: int,
        schedule: dict[str, Any],
        court_ids: list[int],
    ) -> list[TournamentCourtBooking]:
        """
        Create court bookings for tournament based on calculated schedule.

        Args:
            db: Database session
            tournament_id: Tournament ID
            schedule: Calculated tournament schedule
            court_ids: List of court IDs to book

        Returns:
            List of created TournamentCourtBooking objects
        """
        bookings = []

        for time_slot in schedule.get("time_slots", []):
            start_time = datetime.fromisoformat(time_slot["start_time"])
            end_time = datetime.fromisoformat(time_slot["end_time"])

            for court_id in court_ids:
                # Check if court is available
                if court_booking_service.is_court_available(
                    db, court_id, start_time, end_time
                ):
                    booking = TournamentCourtBooking(
                        tournament_id=tournament_id,
                        court_id=court_id,
                        start_time=start_time,
                        end_time=end_time,
                        is_occupied=False,
                    )
                    db.add(booking)
                    bookings.append(booking)

        db.commit()
        return bookings

    def release_tournament_court_bookings(
        self, db: Session, tournament_id: int
    ) -> bool:
        """
        Release all court bookings for a cancelled tournament.

        Args:
            db: Database session
            tournament_id: Tournament ID

        Returns:
            True if successful, False otherwise
        """
        try:
            bookings = (
                db.query(TournamentCourtBooking)
                .filter(TournamentCourtBooking.tournament_id == tournament_id)
                .all()
            )

            for booking in bookings:
                db.delete(booking)

            db.commit()
            return True
        except Exception:
            db.rollback()
            return False

    def get_optimal_court_allocation(
        self,
        db: Session,
        tournament_type: TournamentType,
        categories: list[TournamentCategory],
        participants_per_category: dict[TournamentCategory, int],
        available_courts: list[int],
        time_slots: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Calculate the optimal court allocation for a tournament.

        Args:
            db: Database session
            tournament_type: Type of tournament
            categories: List of tournament categories
            participants_per_category: Number of participants per category
            available_courts: List of available court IDs
            time_slots: List of selected time slots

        Returns:
            Dictionary containing optimal court allocation
        """
        total_matches = 0
        matches_per_category = {}

        for category in categories:
            participant_count = participants_per_category.get(category, 0)
            matches_needed = self._calculate_matches_needed(
                tournament_type, participant_count
            )
            matches_per_category[category] = matches_needed
            total_matches += matches_needed

        # Calculate courts needed per time slot
        total_time_slots = len(time_slots)
        courts_per_slot = min(
            len(available_courts), max(1, total_matches // total_time_slots)
        )

        return {
            "total_matches": total_matches,
            "matches_per_category": matches_per_category,
            "courts_per_slot": courts_per_slot,
            "total_time_slots": total_time_slots,
            "recommended_courts": available_courts[:courts_per_slot],
        }

    def _calculate_matches_needed(
        self, tournament_type: TournamentType, participant_count: int
    ) -> int:
        """Calculate number of matches needed based on tournament type and participants"""
        if participant_count < 2:
            return 0

        if tournament_type == TournamentType.SINGLE_ELIMINATION:
            return participant_count - 1
        if tournament_type == TournamentType.DOUBLE_ELIMINATION:
            return (participant_count - 1) * 2 - 1
        if tournament_type in [
            TournamentType.AMERICANO,
            TournamentType.FIXED_AMERICANO,
        ]:
            # Round-robin: n*(n-1)/2 matches
            return (participant_count * (participant_count - 1)) // 2
        return participant_count - 1

    def _parse_time_slots(
        self, time_slots: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Parse and validate time slots"""
        parsed_slots = []
        for slot in time_slots:
            start_time = datetime.fromisoformat(slot["start_time"])
            end_time = datetime.fromisoformat(slot["end_time"])

            # Ensure slots are hourly
            if (end_time - start_time) != self.slot_duration:
                continue

            parsed_slots.append(
                {
                    "start_time": start_time,
                    "end_time": end_time,
                    "day": start_time.date(),
                    "hour": start_time.hour,
                }
            )

        return sorted(parsed_slots, key=lambda x: x["start_time"])

    def _validate_court_availability(
        self, db: Session, court_ids: list[int], time_slots: list[dict[str, Any]]
    ) -> list[int]:
        """Validate that courts are available for all time slots"""
        available_courts = []

        for court_id in court_ids:
            court_available = True
            for slot in time_slots:
                if not court_booking_service.is_court_available(
                    db, court_id, slot["start_time"], slot["end_time"]
                ):
                    court_available = False
                    break

            if court_available:
                available_courts.append(court_id)

        return available_courts

    def _generate_schedule(
        self,
        tournament_type: TournamentType,
        matches_by_category: dict[TournamentCategory, int],
        time_slots: list[dict[str, Any]],
        available_courts: list[int],
    ) -> dict[str, Any]:
        """Generate the tournament schedule based on tournament type"""
        if tournament_type == TournamentType.AMERICANO:
            return self._generate_americano_schedule(
                matches_by_category, time_slots, available_courts
            )
        if tournament_type == TournamentType.FIXED_AMERICANO:
            return self._generate_fixed_americano_schedule(
                matches_by_category, time_slots, available_courts
            )
        return self._generate_elimination_schedule(
            tournament_type, matches_by_category, time_slots, available_courts
        )

    def _generate_americano_schedule(
        self,
        matches_by_category: dict[TournamentCategory, int],
        time_slots: list[dict[str, Any]],
        available_courts: list[int],
    ) -> dict[str, Any]:
        """Generate schedule for Americano tournament (round-robin with rotation)"""
        schedule = {
            "time_slots": [],
            "court_assignments": {},
            "match_schedule": [],
            "rounds": [],
        }

        total_matches = sum(matches_by_category.values())
        courts_per_slot = len(available_courts)

        # For Americano, we want to distribute matches evenly across rounds
        matches_per_round = courts_per_slot
        total_rounds = max(
            1, (total_matches + matches_per_round - 1) // matches_per_round
        )

        current_match = 0
        for round_num in range(total_rounds):
            if current_match >= total_matches:
                break

            slot_index = round_num % len(time_slots)
            if slot_index >= len(time_slots):
                break

            slot = time_slots[slot_index]
            matches_in_round = min(matches_per_round, total_matches - current_match)

            round_info = {
                "round_number": round_num + 1,
                "start_time": slot["start_time"].isoformat(),
                "end_time": slot["end_time"].isoformat(),
                "matches_scheduled": matches_in_round,
                "courts_used": available_courts[:matches_in_round],
            }

            schedule["rounds"].append(round_info)
            schedule["time_slots"].append(round_info)

            current_match += matches_in_round

        return schedule

    def _generate_fixed_americano_schedule(
        self,
        matches_by_category: dict[TournamentCategory, int],
        time_slots: list[dict[str, Any]],
        available_courts: list[int],
    ) -> dict[str, Any]:
        """Generate schedule for Fixed Americano tournament (predetermined partners)"""
        # Fixed Americano has same scheduling as regular Americano but with fixed partnerships
        return self._generate_americano_schedule(
            matches_by_category, time_slots, available_courts
        )

    def _generate_elimination_schedule(
        self,
        tournament_type: TournamentType,
        matches_by_category: dict[TournamentCategory, int],
        time_slots: list[dict[str, Any]],
        available_courts: list[int],
    ) -> dict[str, Any]:
        """Generate schedule for elimination tournaments"""
        schedule = {
            "time_slots": [],
            "court_assignments": {},
            "match_schedule": [],
            "rounds": [],
        }

        sum(matches_by_category.values())
        courts_per_slot = len(available_courts)

        # For elimination tournaments, matches are organized by rounds
        # Each round must complete before the next begins
        if tournament_type == TournamentType.SINGLE_ELIMINATION:
            rounds_structure = self._calculate_elimination_rounds(
                matches_by_category, False
            )
        else:  # DOUBLE_ELIMINATION
            rounds_structure = self._calculate_elimination_rounds(
                matches_by_category, True
            )

        current_time_slot = 0
        for round_info in rounds_structure:
            if current_time_slot >= len(time_slots):
                break

            matches_in_round = round_info["matches"]
            slots_needed = max(
                1, (matches_in_round + courts_per_slot - 1) // courts_per_slot
            )

            for slot_offset in range(slots_needed):
                slot_index = current_time_slot + slot_offset
                if slot_index >= len(time_slots):
                    break

                slot = time_slots[slot_index]
                matches_in_slot = min(
                    courts_per_slot, matches_in_round - (slot_offset * courts_per_slot)
                )

                if matches_in_slot > 0:
                    round_slot_info = {
                        "round_number": round_info["round_number"],
                        "round_type": round_info.get("round_type", "standard"),
                        "start_time": slot["start_time"].isoformat(),
                        "end_time": slot["end_time"].isoformat(),
                        "matches_scheduled": matches_in_slot,
                        "courts_used": available_courts[:matches_in_slot],
                    }

                    schedule["rounds"].append(round_slot_info)
                    schedule["time_slots"].append(round_slot_info)

            current_time_slot += slots_needed

        return schedule

    def _calculate_elimination_rounds(
        self,
        matches_by_category: dict[TournamentCategory, int],
        is_double_elimination: bool,
    ) -> list[dict[str, Any]]:
        """Calculate the round structure for elimination tournaments"""
        rounds = []

        for category, total_matches in matches_by_category.items():
            if total_matches == 0:
                continue

            if is_double_elimination:
                # Double elimination has winners and losers brackets
                # Simplified calculation for now
                winners_matches = total_matches // 2
                losers_matches = total_matches - winners_matches

                rounds.extend(
                    [
                        {
                            "round_number": 1,
                            "round_type": "winners",
                            "matches": winners_matches,
                            "category": category,
                        },
                        {
                            "round_number": 1,
                            "round_type": "losers",
                            "matches": losers_matches,
                            "category": category,
                        },
                    ]
                )
            else:
                # Single elimination - rounds decrease by half each time
                current_matches = total_matches
                round_num = 1

                while current_matches > 0:
                    rounds.append(
                        {
                            "round_number": round_num,
                            "round_type": "standard",
                            "matches": current_matches,
                            "category": category,
                        }
                    )

                    # Next round has half the matches (winners advance)
                    current_matches = current_matches // 2
                    round_num += 1

                    if current_matches == 1:  # Final match
                        rounds.append(
                            {
                                "round_number": round_num,
                                "round_type": "final",
                                "matches": 1,
                                "category": category,
                            }
                        )
                        break

        return rounds

    def _calculate_estimated_duration(self, schedule: dict[str, Any]) -> int:
        """Calculate estimated tournament duration in hours"""
        time_slots = schedule.get("time_slots", [])
        if not time_slots:
            return 0

        start_time = datetime.fromisoformat(time_slots[0]["start_time"])
        end_time = datetime.fromisoformat(time_slots[-1]["end_time"])

        return int((end_time - start_time).total_seconds() / 3600)

    def get_tournament_schedule_summary(
        self, db: Session, tournament_id: int
    ) -> Optional[dict[str, Any]]:
        """Get a summary of the tournament schedule"""
        tournament = tournament_crud.get_tournament(db, tournament_id)
        if not tournament:
            return None

        court_bookings = tournament.court_bookings
        matches = tournament_crud.get_tournament_matches(db, tournament_id)

        return {
            "tournament_id": tournament_id,
            "tournament_name": tournament.name,
            "total_court_bookings": len(court_bookings),
            "total_matches": len(matches),
            "start_date": tournament.start_date.isoformat(),
            "end_date": tournament.end_date.isoformat(),
            "court_bookings": [
                {
                    "court_id": booking.court_id,
                    "start_time": booking.start_time.isoformat(),
                    "end_time": booking.end_time.isoformat(),
                    "is_occupied": booking.is_occupied,
                }
                for booking in court_bookings
            ],
            "matches_by_status": {
                "scheduled": len([m for m in matches if m.status.value == "SCHEDULED"]),
                "in_progress": len(
                    [m for m in matches if m.status.value == "IN_PROGRESS"]
                ),
                "completed": len([m for m in matches if m.status.value == "COMPLETED"]),
            },
        }


tournament_schedule_service = TournamentScheduleService()
