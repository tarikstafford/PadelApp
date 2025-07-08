from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session, joinedload

from app.models.tournament import (
    CATEGORY_ELO_RANGES,
    RecurringTournament,
    RecurringTournamentCategoryTemplate,
    Tournament,
    TournamentStatus,
)


class RecurringTournamentCRUD:
    def _ensure_correct_elo_ranges(self, category_template_data: dict) -> dict:
        """Ensure category template uses correct ELO ranges from CATEGORY_ELO_RANGES."""
        if "category" in category_template_data:
            from app.models.tournament import TournamentCategory
            category = TournamentCategory(category_template_data["category"])
            if category in CATEGORY_ELO_RANGES:
                min_elo, max_elo = CATEGORY_ELO_RANGES[category]
                category_template_data["min_elo"] = min_elo
                category_template_data["max_elo"] = max_elo
        return category_template_data
    def create_recurring_tournament(
        self, db: Session, recurring_tournament_data: dict
    ) -> RecurringTournament:
        """Create a new recurring tournament."""
        recurring_tournament = RecurringTournament(**recurring_tournament_data)
        db.add(recurring_tournament)
        db.commit()
        db.refresh(recurring_tournament)
        return recurring_tournament

    def get_recurring_tournament(
        self, db: Session, recurring_tournament_id: int
    ) -> Optional[RecurringTournament]:
        """Get a recurring tournament by ID."""
        return (
            db.query(RecurringTournament)
            .options(joinedload(RecurringTournament.category_templates))
            .filter(RecurringTournament.id == recurring_tournament_id)
            .first()
        )

    def get_recurring_tournaments(
        self,
        db: Session,
        club_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[RecurringTournament]:
        """Get multiple recurring tournaments with optional filtering."""
        query = db.query(RecurringTournament).options(
            joinedload(RecurringTournament.category_templates)
        )

        if club_id is not None:
            query = query.filter(RecurringTournament.club_id == club_id)

        if is_active is not None:
            query = query.filter(RecurringTournament.is_active == is_active)

        return query.offset(skip).limit(limit).all()

    def update_recurring_tournament(
        self,
        db: Session,
        recurring_tournament_id: int,
        update_data: dict,
    ) -> Optional[RecurringTournament]:
        """Update a recurring tournament."""
        recurring_tournament = (
            db.query(RecurringTournament)
            .filter(RecurringTournament.id == recurring_tournament_id)
            .first()
        )

        if not recurring_tournament:
            return None

        for key, value in update_data.items():
            if hasattr(recurring_tournament, key):
                setattr(recurring_tournament, key, value)

        recurring_tournament.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(recurring_tournament)
        return recurring_tournament

    def delete_recurring_tournament(
        self, db: Session, recurring_tournament_id: int
    ) -> bool:
        """Delete a recurring tournament and all its instances."""
        recurring_tournament = (
            db.query(RecurringTournament)
            .filter(RecurringTournament.id == recurring_tournament_id)
            .first()
        )

        if not recurring_tournament:
            return False

        # Delete all associated tournament instances
        db.query(Tournament).filter(
            Tournament.recurring_tournament_id == recurring_tournament_id
        ).delete()

        # Delete the recurring tournament
        db.delete(recurring_tournament)
        db.commit()
        return True

    def create_category_template(
        self, db: Session, category_template_data: dict
    ) -> RecurringTournamentCategoryTemplate:
        """Create a category template for a recurring tournament."""
        # Ensure correct ELO ranges
        category_template_data = self._ensure_correct_elo_ranges(category_template_data)
        category_template = RecurringTournamentCategoryTemplate(
            **category_template_data
        )
        db.add(category_template)
        db.commit()
        db.refresh(category_template)
        return category_template

    def get_category_templates(
        self, db: Session, recurring_tournament_id: int
    ) -> list[RecurringTournamentCategoryTemplate]:
        """Get all category templates for a recurring tournament."""
        return (
            db.query(RecurringTournamentCategoryTemplate)
            .filter(
                RecurringTournamentCategoryTemplate.recurring_tournament_id
                == recurring_tournament_id
            )
            .all()
        )

    def update_category_template(
        self,
        db: Session,
        category_template_id: int,
        update_data: dict,
    ) -> Optional[RecurringTournamentCategoryTemplate]:
        """Update a category template."""
        category_template = (
            db.query(RecurringTournamentCategoryTemplate)
            .filter(RecurringTournamentCategoryTemplate.id == category_template_id)
            .first()
        )

        if not category_template:
            return None

        for key, value in update_data.items():
            if hasattr(category_template, key):
                setattr(category_template, key, value)

        db.commit()
        db.refresh(category_template)
        return category_template

    def delete_category_template(self, db: Session, category_template_id: int) -> bool:
        """Delete a category template."""
        category_template = (
            db.query(RecurringTournamentCategoryTemplate)
            .filter(RecurringTournamentCategoryTemplate.id == category_template_id)
            .first()
        )

        if not category_template:
            return False

        db.delete(category_template)
        db.commit()
        return True

    def get_tournament_instances(
        self,
        db: Session,
        recurring_tournament_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status_filter: Optional[list[TournamentStatus]] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Tournament]:
        """Get tournament instances for a recurring tournament."""
        query = db.query(Tournament).filter(
            Tournament.recurring_tournament_id == recurring_tournament_id
        )

        if start_date:
            query = query.filter(Tournament.start_date >= start_date)

        if end_date:
            query = query.filter(Tournament.start_date <= end_date)

        if status_filter:
            query = query.filter(Tournament.status.in_(status_filter))

        return query.order_by(Tournament.start_date).offset(skip).limit(limit).all()

    def get_recurring_tournaments_by_club(
        self,
        db: Session,
        club_id: int,
        is_active: bool = True,
        skip: int = 0,
        limit: int = 100,
    ) -> list[RecurringTournament]:
        """Get all recurring tournaments for a specific club."""
        query = (
            db.query(RecurringTournament)
            .options(joinedload(RecurringTournament.category_templates))
            .filter(RecurringTournament.club_id == club_id)
        )

        if is_active is not None:
            query = query.filter(RecurringTournament.is_active == is_active)

        return (
            query.order_by(RecurringTournament.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_active_recurring_tournaments(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> list[RecurringTournament]:
        """Get all active recurring tournaments."""
        return (
            db.query(RecurringTournament)
            .options(joinedload(RecurringTournament.category_templates))
            .filter(RecurringTournament.is_active.is_(True))
            .filter(RecurringTournament.auto_generation_enabled.is_(True))
            .order_by(RecurringTournament.series_start_date)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_tournament_instances(
        self,
        db: Session,
        recurring_tournament_id: int,
        status_filter: Optional[list[TournamentStatus]] = None,
    ) -> int:
        """Count tournament instances for a recurring tournament."""
        query = db.query(Tournament).filter(
            Tournament.recurring_tournament_id == recurring_tournament_id
        )

        if status_filter:
            query = query.filter(Tournament.status.in_(status_filter))

        return query.count()

    def bulk_update_category_templates(
        self,
        db: Session,
        recurring_tournament_id: int,
        category_templates_data: list[dict],
    ) -> list[RecurringTournamentCategoryTemplate]:
        """Bulk update category templates for a recurring tournament."""
        # Delete existing templates
        db.query(RecurringTournamentCategoryTemplate).filter(
            RecurringTournamentCategoryTemplate.recurring_tournament_id
            == recurring_tournament_id
        ).delete()

        # Create new templates
        new_templates = []
        for template_data in category_templates_data:
            template_data["recurring_tournament_id"] = recurring_tournament_id
            # Ensure correct ELO ranges
            template_data = self._ensure_correct_elo_ranges(template_data)
            template = RecurringTournamentCategoryTemplate(**template_data)
            db.add(template)
            new_templates.append(template)

        db.commit()

        # Refresh all templates
        for template in new_templates:
            db.refresh(template)

        return new_templates


# Create CRUD instance
recurring_tournament_crud = RecurringTournamentCRUD()
