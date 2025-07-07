from datetime import datetime, timedelta
from typing import Optional

from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session

from app.crud.tournament_crud import tournament_crud
from app.models.tournament import (
    RecurrencePattern,
    RecurringTournament,
    RecurringTournamentCategoryTemplate,
    Tournament,
    TournamentCategoryConfig,
    TournamentStatus,
)


class RecurringTournamentService:
    def __init__(self):
        pass

    def generate_tournament_instances(
        self,
        db: Session,
        recurring_tournament_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 10,
    ) -> list[Tournament]:
        """
        Generate tournament instances for a recurring tournament within a date range.

        Args:
            db: Database session
            recurring_tournament_id: ID of the recurring tournament
            start_date: Start date for generation (defaults to now)
            end_date: End date for generation (defaults to advance_generation_days from now)
            limit: Maximum number of tournaments to generate

        Returns:
            List of created tournament instances
        """
        recurring_tournament = (
            db.query(RecurringTournament)
            .filter(RecurringTournament.id == recurring_tournament_id)
            .first()
        )

        if not recurring_tournament or not recurring_tournament.is_active:
            return []

        # Set default dates if not provided
        if start_date is None:
            start_date = datetime.utcnow()

        if end_date is None:
            end_date = start_date + timedelta(
                days=recurring_tournament.advance_generation_days
            )

        # Don't generate beyond series end date
        if (
            recurring_tournament.series_end_date
            and end_date > recurring_tournament.series_end_date
        ):
            end_date = recurring_tournament.series_end_date

        # Calculate occurrence dates
        occurrence_dates = self._calculate_occurrence_dates(
            recurring_tournament, start_date, end_date, limit
        )

        # Get existing tournament instances to avoid duplicates
        existing_tournaments = (
            db.query(Tournament)
            .filter(Tournament.recurring_tournament_id == recurring_tournament_id)
            .filter(Tournament.start_date >= start_date)
            .filter(Tournament.start_date <= end_date)
            .all()
        )

        existing_dates = {t.start_date.date() for t in existing_tournaments}

        # Create new tournament instances
        created_tournaments = []
        for occurrence_date in occurrence_dates:
            if occurrence_date.date() not in existing_dates:
                tournament = self._create_tournament_instance(
                    db, recurring_tournament, occurrence_date
                )
                if tournament:
                    created_tournaments.append(tournament)

        return created_tournaments

    def _calculate_occurrence_dates(
        self,
        recurring_tournament: RecurringTournament,
        start_date: datetime,
        end_date: datetime,
        limit: int,
    ) -> list[datetime]:
        """Calculate occurrence dates based on recurrence pattern."""
        occurrence_dates = []
        current_date = max(start_date, recurring_tournament.series_start_date)

        count = 0
        while current_date <= end_date and count < limit:
            if recurring_tournament.recurrence_pattern == RecurrencePattern.WEEKLY:
                dates = self._calculate_weekly_occurrences(
                    recurring_tournament, current_date, end_date
                )
            elif recurring_tournament.recurrence_pattern == RecurrencePattern.MONTHLY:
                dates = self._calculate_monthly_occurrences(
                    recurring_tournament, current_date, end_date
                )
            else:  # CUSTOM
                dates = self._calculate_custom_occurrences(
                    recurring_tournament, current_date, end_date
                )

            for date in dates:
                if date <= end_date and count < limit:
                    occurrence_dates.append(date)
                    count += 1
                else:
                    break

            break  # The calculation methods handle the full range

        return occurrence_dates[:limit]

    def _calculate_weekly_occurrences(
        self,
        recurring_tournament: RecurringTournament,
        start_date: datetime,
        end_date: datetime,
    ) -> list[datetime]:
        """Calculate weekly occurrences based on days_of_week."""
        occurrences = []

        # Get days of week (0=Monday, 6=Sunday)
        days_of_week = recurring_tournament.days_of_week or []
        if not days_of_week:
            # Default to the same day of week as series start
            days_of_week = [recurring_tournament.series_start_date.weekday()]

        # Start from the series start date
        current_date = recurring_tournament.series_start_date

        # Find the first occurrence on or after start_date
        while current_date < start_date:
            current_date += timedelta(days=1)
            if current_date.weekday() in days_of_week:
                break

        # Generate occurrences
        weeks_passed = 0
        while current_date <= end_date:
            if current_date.weekday() in days_of_week:
                # Check if this matches the interval (every X weeks)
                if weeks_passed % recurring_tournament.interval_value == 0:
                    occurrence_time = current_date.replace(
                        hour=recurring_tournament.series_start_date.hour,
                        minute=recurring_tournament.series_start_date.minute,
                        second=0,
                        microsecond=0,
                    )
                    if occurrence_time >= start_date:
                        occurrences.append(occurrence_time)

                # Move to next week after processing this day
                if current_date.weekday() == max(days_of_week):
                    weeks_passed += 1
                    current_date += timedelta(days=7 - current_date.weekday())
                else:
                    current_date += timedelta(days=1)
            else:
                current_date += timedelta(days=1)

        return occurrences

    def _calculate_monthly_occurrences(
        self,
        recurring_tournament: RecurringTournament,
        start_date: datetime,
        end_date: datetime,
    ) -> list[datetime]:
        """Calculate monthly occurrences."""
        occurrences = []

        # Use day_of_month or default to series start day
        target_day = (
            recurring_tournament.day_of_month
            or recurring_tournament.series_start_date.day
        )

        # Start from series start date
        current_date = recurring_tournament.series_start_date

        # Find first occurrence on or after start_date
        while current_date < start_date:
            current_date += relativedelta(months=1)
            # Handle month-end edge cases
            if target_day > 28:
                current_date = current_date.replace(day=min(target_day, 28))
                # Then add days to get to target day if possible
                last_day = (current_date + relativedelta(months=1, days=-1)).day
                if target_day <= last_day:
                    current_date = current_date.replace(day=target_day)
            else:
                current_date = current_date.replace(day=target_day)

        # Generate occurrences
        months_passed = 0
        while current_date <= end_date:
            if months_passed % recurring_tournament.interval_value == 0:
                occurrence_time = current_date.replace(
                    hour=recurring_tournament.series_start_date.hour,
                    minute=recurring_tournament.series_start_date.minute,
                    second=0,
                    microsecond=0,
                )
                if occurrence_time >= start_date:
                    occurrences.append(occurrence_time)

            # Move to next month
            current_date += relativedelta(months=1)
            months_passed += 1

            # Handle month-end edge cases
            if target_day > 28:
                last_day = (current_date + relativedelta(months=1, days=-1)).day
                if target_day <= last_day:
                    current_date = current_date.replace(day=target_day)
                else:
                    current_date = current_date.replace(day=last_day)

        return occurrences

    def _calculate_custom_occurrences(
        self,
        recurring_tournament: RecurringTournament,
        start_date: datetime,
        end_date: datetime,
    ) -> list[datetime]:
        """Calculate custom occurrences (placeholder for future implementation)."""
        # For now, treat custom as weekly with default settings
        return self._calculate_weekly_occurrences(
            recurring_tournament, start_date, end_date
        )

    def _create_tournament_instance(
        self,
        db: Session,
        recurring_tournament: RecurringTournament,
        start_date: datetime,
    ) -> Optional[Tournament]:
        """Create a single tournament instance from recurring tournament template."""

        # Calculate tournament end date
        end_date = start_date + timedelta(hours=recurring_tournament.duration_hours)

        # Calculate registration deadline
        registration_deadline = start_date - timedelta(
            hours=recurring_tournament.registration_deadline_hours
        )

        # Generate tournament name with date
        tournament_name = (
            f"{recurring_tournament.series_name} - {start_date.strftime('%Y-%m-%d')}"
        )

        # Create tournament instance
        tournament_data = {
            "club_id": recurring_tournament.club_id,
            "recurring_tournament_id": recurring_tournament.id,
            "name": tournament_name,
            "description": recurring_tournament.description,
            "tournament_type": recurring_tournament.tournament_type,
            "start_date": start_date,
            "end_date": end_date,
            "registration_deadline": registration_deadline,
            "status": TournamentStatus.DRAFT,
            "max_participants": recurring_tournament.max_participants,
            "entry_fee": recurring_tournament.entry_fee,
        }

        tournament = tournament_crud.create_tournament_from_dict(db, tournament_data)

        if tournament:
            # Create category configs from templates
            self._create_category_configs_from_templates(
                db, tournament.id, recurring_tournament.category_templates
            )

        return tournament

    def _create_category_configs_from_templates(
        self,
        db: Session,
        tournament_id: int,
        category_templates: list[RecurringTournamentCategoryTemplate],
    ) -> None:
        """Create tournament category configs from recurring tournament templates."""
        for template in category_templates:
            category_config = TournamentCategoryConfig(
                tournament_id=tournament_id,
                category=template.category,
                max_participants=template.max_participants,
                min_elo=template.min_elo,
                max_elo=template.max_elo,
            )
            db.add(category_config)

        db.commit()

    def get_next_occurrences(
        self,
        db: Session,
        recurring_tournament_id: int,
        count: int = 5,
    ) -> list[datetime]:
        """Get the next N occurrence dates for a recurring tournament."""
        recurring_tournament = (
            db.query(RecurringTournament)
            .filter(RecurringTournament.id == recurring_tournament_id)
            .first()
        )

        if not recurring_tournament:
            return []

        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=365)  # Look ahead 1 year

        return self._calculate_occurrence_dates(
            recurring_tournament, start_date, end_date, count
        )

    def update_recurring_tournament(
        self,
        db: Session,
        recurring_tournament_id: int,
        update_data: dict,
    ) -> Optional[RecurringTournament]:
        """
        Update a recurring tournament. Only affects future tournament instances.
        """
        recurring_tournament = (
            db.query(RecurringTournament)
            .filter(RecurringTournament.id == recurring_tournament_id)
            .first()
        )

        if not recurring_tournament:
            return None

        # Update the recurring tournament
        for key, value in update_data.items():
            if hasattr(recurring_tournament, key):
                setattr(recurring_tournament, key, value)

        recurring_tournament.updated_at = datetime.utcnow()
        db.commit()

        return recurring_tournament

    def cancel_recurring_tournament(
        self,
        db: Session,
        recurring_tournament_id: int,
        cancel_future_only: bool = True,
    ) -> bool:
        """
        Cancel a recurring tournament series.

        Args:
            db: Database session
            recurring_tournament_id: ID of recurring tournament to cancel
            cancel_future_only: If True, only cancel future instances. If False, cancel all.

        Returns:
            True if successful, False otherwise
        """
        recurring_tournament = (
            db.query(RecurringTournament)
            .filter(RecurringTournament.id == recurring_tournament_id)
            .first()
        )

        if not recurring_tournament:
            return False

        # Mark recurring tournament as inactive
        recurring_tournament.is_active = False
        recurring_tournament.updated_at = datetime.utcnow()

        if cancel_future_only:
            # Cancel only future tournament instances
            cutoff_date = datetime.utcnow()
            future_tournaments = (
                db.query(Tournament)
                .filter(Tournament.recurring_tournament_id == recurring_tournament_id)
                .filter(Tournament.start_date > cutoff_date)
                .filter(
                    Tournament.status.in_(
                        [TournamentStatus.DRAFT, TournamentStatus.REGISTRATION_OPEN]
                    )
                )
                .all()
            )

            for tournament in future_tournaments:
                tournament.status = TournamentStatus.CANCELLED
                tournament.updated_at = datetime.utcnow()
        else:
            # Cancel all tournament instances
            all_tournaments = (
                db.query(Tournament)
                .filter(Tournament.recurring_tournament_id == recurring_tournament_id)
                .filter(Tournament.status != TournamentStatus.COMPLETED)
                .all()
            )

            for tournament in all_tournaments:
                tournament.status = TournamentStatus.CANCELLED
                tournament.updated_at = datetime.utcnow()

        db.commit()
        return True

    def get_tournament_instances(
        self,
        db: Session,
        recurring_tournament_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        include_cancelled: bool = False,
    ) -> list[Tournament]:
        """Get tournament instances for a recurring tournament."""
        query = db.query(Tournament).filter(
            Tournament.recurring_tournament_id == recurring_tournament_id
        )

        if start_date:
            query = query.filter(Tournament.start_date >= start_date)

        if end_date:
            query = query.filter(Tournament.start_date <= end_date)

        if not include_cancelled:
            query = query.filter(Tournament.status != TournamentStatus.CANCELLED)

        return query.order_by(Tournament.start_date).all()


# Create service instance
recurring_tournament_service = RecurringTournamentService()
