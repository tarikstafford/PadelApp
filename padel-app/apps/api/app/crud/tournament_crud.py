import contextlib
import logging
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import and_, desc
from sqlalchemy.orm import Session, joinedload

from app.models.team import Team
from app.models.tournament import (
    CATEGORY_ELO_RANGES,
    MatchStatus,
    Tournament,
    TournamentCategory,
    TournamentCategoryConfig,
    TournamentCourtBooking,
    TournamentMatch,
    TournamentParticipant,
    TournamentStatus,
    TournamentTeam,
    TournamentTrophy,
    TournamentType,
)
from app.models.user import User
from app.schemas.tournament_schemas import (
    TournamentCreate,
    TournamentMatchCreate,
    TournamentMatchUpdate,
    TournamentTeamCreate,
    TournamentUpdate,
)


class TournamentCRUD:
    def _is_elo_eligible_for_category(
        self, elo_rating: float, category_config: TournamentCategoryConfig
    ) -> bool:
        """Check if an ELO rating is eligible for a tournament category.

        Handles PLATINUM category specially since it should accept any ELO >= 5.0
        """
        if category_config.category == TournamentCategory.PLATINUM:
            # For PLATINUM, accept any ELO >= min_elo (no upper bound)
            return elo_rating >= category_config.min_elo
        # For other categories, use standard range check
        return category_config.min_elo <= elo_rating < category_config.max_elo

    def create_tournament(
        self, db: Session, tournament_data: TournamentCreate, club_id: int
    ) -> Tournament:
        # Validate that at least one category is provided
        if not tournament_data.categories:
            raise ValueError("Tournament must have at least one category")

        # Calculate total max participants as sum of category limits
        total_max_participants = sum(
            cat.max_participants for cat in tournament_data.categories
        )

        # Create tournament
        tournament = Tournament(
            club_id=club_id,
            name=tournament_data.name,
            description=tournament_data.description,
            tournament_type=tournament_data.tournament_type,
            start_date=tournament_data.start_date,
            end_date=tournament_data.end_date,
            registration_deadline=tournament_data.registration_deadline,
            max_participants=total_max_participants,  # Sum of category limits
            entry_fee=tournament_data.entry_fee or 0.0,
            status=TournamentStatus.DRAFT,
        )
        db.add(tournament)
        db.flush()  # Get the tournament ID

        # Create category configurations
        for category_data in tournament_data.categories:
            elo_range = CATEGORY_ELO_RANGES[category_data.category]
            category_config = TournamentCategoryConfig(
                tournament_id=tournament.id,
                category=category_data.category,
                max_participants=category_data.max_participants,
                min_elo=elo_range[0],
                max_elo=elo_range[1],
            )
            db.add(category_config)

        # Block courts for tournament dates
        for court_id in tournament_data.court_ids:
            court_booking = TournamentCourtBooking(
                tournament_id=tournament.id,
                court_id=court_id,
                start_time=tournament_data.start_date,
                end_time=tournament_data.end_date,
            )
            db.add(court_booking)

        db.commit()
        db.refresh(tournament)
        return tournament

    def create_tournament_from_dict(
        self, db: Session, tournament_data: dict
    ) -> Tournament:
        """Create tournament from dictionary data.

        Used by recurring tournament service.
        """
        tournament = Tournament(**tournament_data)
        db.add(tournament)
        db.commit()
        db.refresh(tournament)
        return tournament

    def get_tournament(self, db: Session, tournament_id: int) -> Optional[Tournament]:
        try:
            return (
                db.query(Tournament)
                .options(
                    joinedload(Tournament.categories),
                    joinedload(Tournament.teams).joinedload(TournamentTeam.team),
                    joinedload(Tournament.matches),
                    joinedload(Tournament.court_bookings),
                )
                .filter(Tournament.id == tournament_id)
                .first()
            )
        except Exception:
            # Fallback without eager loading if relationships fail
            try:
                tournament = (
                    db.query(Tournament).filter(Tournament.id == tournament_id).first()
                )
                if tournament:
                    # Try to load essential relationships separately
                    with contextlib.suppress(Exception):
                        _ = tournament.categories
                    with contextlib.suppress(Exception):
                        _ = tournament.teams
            except Exception:
                return None
            else:
                return tournament

    def get_tournaments_by_club(
        self, db: Session, club_id: int, skip: int = 0, limit: int = 100
    ) -> list[Tournament]:
        return (
            db.query(Tournament)
            .options(joinedload(Tournament.club))
            .filter(Tournament.club_id == club_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_tournaments_by_status(
        self, db: Session, status: TournamentStatus, skip: int = 0, limit: int = 100
    ) -> list[Tournament]:
        return (
            db.query(Tournament)
            .filter(Tournament.status == status)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_tournaments(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> list[Tournament]:
        return (
            db.query(Tournament)
            .options(joinedload(Tournament.club))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update_tournament(
        self, db: Session, tournament_id: int, tournament_data: TournamentUpdate
    ) -> Optional[Tournament]:
        tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
        if not tournament:
            return None

        update_data = tournament_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(tournament, field, value)

        tournament.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(tournament)
        return tournament

    def delete_tournament(self, db: Session, tournament_id: int) -> bool:
        tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
        if not tournament:
            return False

        db.delete(tournament)
        db.commit()
        return True

    def register_team(
        self, db: Session, tournament_id: int, team_data: TournamentTeamCreate
    ) -> Optional[TournamentTeam]:
        # Check tournament exists and is open for registration
        tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
        if not tournament or tournament.status != TournamentStatus.REGISTRATION_OPEN:
            return None

        # Get category config
        category_config = (
            db.query(TournamentCategoryConfig)
            .filter(
                and_(
                    TournamentCategoryConfig.tournament_id == tournament_id,
                    TournamentCategoryConfig.category == team_data.category,
                )
            )
            .first()
        )
        if not category_config:
            return None

        # Check if team is already registered
        existing_registration = (
            db.query(TournamentTeam)
            .filter(
                and_(
                    TournamentTeam.tournament_id == tournament_id,
                    TournamentTeam.team_id == team_data.team_id,
                )
            )
            .first()
        )
        if existing_registration:
            return None

        # Get team and calculate average ELO
        team = (
            db.query(Team)
            .options(joinedload(Team.players))
            .filter(Team.id == team_data.team_id)
            .first()
        )
        if (
            not team or len(team.players) != 2
        ):  # Padel teams must have exactly 2 players
            return None

        average_elo = sum(player.elo_rating for player in team.players) / len(
            team.players
        )

        # Check ELO eligibility
        if not self._is_elo_eligible_for_category(average_elo, category_config):
            return None

        # Check category capacity
        current_teams = (
            db.query(TournamentTeam)
            .filter(TournamentTeam.category_config_id == category_config.id)
            .count()
        )
        if current_teams >= category_config.max_participants:
            return None

        # Register team
        tournament_team = TournamentTeam(
            tournament_id=tournament_id,
            category_config_id=category_config.id,
            team_id=team_data.team_id,
            average_elo=average_elo,
        )
        db.add(tournament_team)
        db.commit()
        db.refresh(tournament_team)
        return tournament_team

    def unregister_team(self, db: Session, tournament_id: int, team_id: int) -> bool:
        tournament_team = (
            db.query(TournamentTeam)
            .filter(
                and_(
                    TournamentTeam.tournament_id == tournament_id,
                    TournamentTeam.team_id == team_id,
                )
            )
            .first()
        )
        if not tournament_team:
            return False

        db.delete(tournament_team)
        db.commit()
        return True

    def register_participant(
        self,
        db: Session,
        tournament_id: int,
        user_id: int,
        category: TournamentCategory,
    ) -> Optional[TournamentParticipant]:
        """Register an individual participant for Americano tournaments"""
        # Check tournament exists and is open for registration
        tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
        if not tournament or tournament.status != TournamentStatus.REGISTRATION_OPEN:
            return None

        # Check if tournament type supports individual registration
        if tournament.tournament_type not in [
            TournamentType.AMERICANO,
            TournamentType.FIXED_AMERICANO,
        ]:
            return None

        # Get category config
        category_config = (
            db.query(TournamentCategoryConfig)
            .filter(
                and_(
                    TournamentCategoryConfig.tournament_id == tournament_id,
                    TournamentCategoryConfig.category == category,
                )
            )
            .first()
        )
        if not category_config:
            return None

        # Check if participant is already registered
        existing_registration = (
            db.query(TournamentParticipant)
            .filter(
                and_(
                    TournamentParticipant.tournament_id == tournament_id,
                    TournamentParticipant.user_id == user_id,
                )
            )
            .first()
        )
        if existing_registration:
            return None

        # Get user and check ELO eligibility
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        if not self._is_elo_eligible_for_category(user.elo_rating, category_config):
            return None

        # Check category capacity
        try:
            current_participants = (
                db.query(TournamentParticipant)
                .filter(TournamentParticipant.category_config_id == category_config.id)
                .count()
            )
            if current_participants >= category_config.max_participants:
                return None
        except Exception:
            # Table might not exist yet, allow registration
            logging.debug("TournamentParticipant table might not exist yet")

        # Register participant
        try:
            tournament_participant = TournamentParticipant(
                tournament_id=tournament_id,
                category_config_id=category_config.id,
                user_id=user_id,
                elo_at_registration=user.elo_rating,
            )
        except Exception:
            # Table might not exist yet
            return None

        try:
            db.add(tournament_participant)
            db.commit()
            db.refresh(tournament_participant)
        except Exception:
            db.rollback()
            return None
        else:
            return tournament_participant

    def unregister_participant(
        self, db: Session, tournament_id: int, user_id: int
    ) -> bool:
        """Unregister an individual participant from Americano tournament"""
        tournament_participant = (
            db.query(TournamentParticipant)
            .filter(
                and_(
                    TournamentParticipant.tournament_id == tournament_id,
                    TournamentParticipant.user_id == user_id,
                )
            )
            .first()
        )
        if not tournament_participant:
            return False

        db.delete(tournament_participant)
        db.commit()
        return True

    def get_tournament_participants(
        self,
        db: Session,
        tournament_id: int,
        category: Optional[TournamentCategory] = None,
    ) -> list[TournamentParticipant]:
        """Get individual participants for Americano tournaments"""
        try:
            query = (
                db.query(TournamentParticipant)
                .options(
                    joinedload(TournamentParticipant.user),
                    joinedload(TournamentParticipant.category_config),
                )
                .filter(TournamentParticipant.tournament_id == tournament_id)
            )
        except Exception:
            # Return empty list if participants table doesn't exist yet
            return []

        try:
            if category:
                query = query.join(TournamentCategoryConfig).filter(
                    TournamentCategoryConfig.category == category
                )

            return query.all()
        except Exception:
            return []

    def get_tournament_teams(
        self,
        db: Session,
        tournament_id: int,
        category: Optional[TournamentCategory] = None,
    ) -> list[TournamentTeam]:
        query = (
            db.query(TournamentTeam)
            .options(
                joinedload(TournamentTeam.team).joinedload(Team.players),
                joinedload(TournamentTeam.category_config),
            )
            .filter(TournamentTeam.tournament_id == tournament_id)
        )

        if category:
            query = query.join(TournamentCategoryConfig).filter(
                TournamentCategoryConfig.category == category
            )

        return query.all()

    def create_match(
        self,
        db: Session,
        tournament_id: int,
        category_config_id: int,
        match_data: TournamentMatchCreate,
    ) -> TournamentMatch:
        match = TournamentMatch(
            tournament_id=tournament_id,
            category_config_id=category_config_id,
            team1_id=match_data.team1_id,
            team2_id=match_data.team2_id,
            round_number=match_data.round_number,
            match_number=match_data.match_number,
            scheduled_time=match_data.scheduled_time,
            court_id=match_data.court_id,
        )
        db.add(match)
        db.commit()
        db.refresh(match)
        return match

    def update_match(
        self, db: Session, match_id: int, match_data: TournamentMatchUpdate
    ) -> Optional[TournamentMatch]:
        match = db.query(TournamentMatch).filter(TournamentMatch.id == match_id).first()
        if not match:
            return None

        update_data = match_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(match, field, value)

        match.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(match)
        return match

    def get_tournament_matches(
        self,
        db: Session,
        tournament_id: int,
        category: Optional[TournamentCategory] = None,
    ) -> list[TournamentMatch]:
        query = (
            db.query(TournamentMatch)
            .options(
                joinedload(TournamentMatch.team1).joinedload(TournamentTeam.team),
                joinedload(TournamentMatch.team2).joinedload(TournamentTeam.team),
                joinedload(TournamentMatch.court),
                joinedload(TournamentMatch.category_config),
            )
            .filter(TournamentMatch.tournament_id == tournament_id)
        )

        if category:
            query = query.join(TournamentCategoryConfig).filter(
                TournamentCategoryConfig.category == category
            )

        return query.order_by(
            TournamentMatch.round_number, TournamentMatch.match_number
        ).all()

    def get_match(self, db: Session, match_id: int) -> Optional[TournamentMatch]:
        return (
            db.query(TournamentMatch)
            .options(
                joinedload(TournamentMatch.team1).joinedload(TournamentTeam.team),
                joinedload(TournamentMatch.team2).joinedload(TournamentTeam.team),
                joinedload(TournamentMatch.court),
            )
            .filter(TournamentMatch.id == match_id)
            .first()
        )

    def get_upcoming_matches(
        self, db: Session, club_id: int, limit: int = 10
    ) -> list[TournamentMatch]:
        return (
            db.query(TournamentMatch)
            .join(Tournament)
            .filter(
                and_(
                    Tournament.club_id == club_id,
                    TournamentMatch.scheduled_time > datetime.now(timezone.utc),
                    TournamentMatch.status == MatchStatus.SCHEDULED,
                )
            )
            .order_by(TournamentMatch.scheduled_time)
            .limit(limit)
            .all()
        )

    def check_team_eligibility(
        self, db: Session, tournament_id: int, team_id: int
    ) -> dict[str, Any]:
        tournament = (
            db.query(Tournament)
            .options(joinedload(Tournament.categories))
            .filter(Tournament.id == tournament_id)
            .first()
        )
        if not tournament:
            return {"eligible": False, "reason": "Tournament not found"}

        # Check if tournament requires teams
        if tournament.tournament_type in [
            TournamentType.AMERICANO,
            TournamentType.FIXED_AMERICANO,
        ]:
            return {
                "eligible": False,
                "reason": "This tournament accepts individual registrations, not teams",
            }

        team = (
            db.query(Team)
            .options(joinedload(Team.players))
            .filter(Team.id == team_id)
            .first()
        )
        if not team:
            return {"eligible": False, "reason": "Team not found"}

        if len(team.players) != 2:
            return {"eligible": False, "reason": "Team must have exactly 2 players"}

        average_elo = sum(player.elo_rating for player in team.players) / len(
            team.players
        )
        eligible_categories = []
        reasons = []

        for category_config in tournament.categories:
            if self._is_elo_eligible_for_category(average_elo, category_config):
                # Check capacity
                current_teams = (
                    db.query(TournamentTeam)
                    .filter(TournamentTeam.category_config_id == category_config.id)
                    .count()
                )
                if current_teams < category_config.max_participants:
                    eligible_categories.append(category_config.category)
                else:
                    reasons.append(
                        f"{category_config.category} category is full "
                        f"({current_teams}/{category_config.max_participants})"
                    )

        # If no eligible categories, provide specific reasons
        if not eligible_categories:
            if not reasons:  # No categories matched ELO range
                reasons.append(
                    f"Team average ELO ({average_elo:.1f}) doesn't match any "
                    f"tournament category ranges"
                )

            return {
                "eligible": False,
                "reason": "; ".join(reasons),
                "average_elo": average_elo,
                "team_players": [
                    {"id": p.id, "name": p.full_name, "elo": p.elo_rating}
                    for p in team.players
                ],
            }

        return {
            "eligible": len(eligible_categories) > 0,
            "eligible_categories": eligible_categories,
            "average_elo": average_elo,
            "team_players": [
                {"id": p.id, "name": p.full_name, "elo": p.elo_rating}
                for p in team.players
            ],
        }

    def check_participant_eligibility(
        self, db: Session, tournament_id: int, user_id: int
    ) -> dict[str, Any]:
        """Check if a user is eligible for individual registration.

        Applies to Americano tournaments.
        """
        tournament = (
            db.query(Tournament)
            .options(joinedload(Tournament.categories))
            .filter(Tournament.id == tournament_id)
            .first()
        )
        if not tournament:
            return {"eligible": False, "reason": "Tournament not found"}

        # Check if tournament accepts individual registrations
        if tournament.tournament_type not in [
            TournamentType.AMERICANO,
            TournamentType.FIXED_AMERICANO,
        ]:
            return {
                "eligible": False,
                "reason": "This tournament requires team registration",
            }

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"eligible": False, "reason": "User not found"}

        eligible_categories = []
        reasons = []

        for category_config in tournament.categories:
            if self._is_elo_eligible_for_category(user.elo_rating, category_config):
                # Check capacity
                current_participants = (
                    db.query(TournamentParticipant)
                    .filter(
                        TournamentParticipant.category_config_id == category_config.id
                    )
                    .count()
                )
                if current_participants < category_config.max_participants:
                    eligible_categories.append(category_config.category)
                else:
                    reasons.append(
                        f"{category_config.category} category is full "
                        f"({current_participants}/{category_config.max_participants})"
                    )

        # If no eligible categories, provide specific reasons
        if not eligible_categories:
            if not reasons:  # No categories matched ELO range
                reasons.append(
                    f"User ELO ({user.elo_rating:.1f}) doesn't match any "
                    f"tournament category ranges"
                )

            return {
                "eligible": False,
                "reason": "; ".join(reasons),
                "elo_rating": user.elo_rating,
                "user": {"id": user.id, "name": user.full_name, "elo": user.elo_rating},
            }

        return {
            "eligible": len(eligible_categories) > 0,
            "eligible_categories": eligible_categories,
            "elo_rating": user.elo_rating,
            "user": {"id": user.id, "name": user.full_name, "elo": user.elo_rating},
        }

    def get_tournament_stats(
        self, db: Session, tournament_id: int
    ) -> Optional[dict[str, Any]]:
        tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
        if not tournament:
            return None

        total_matches = (
            db.query(TournamentMatch)
            .filter(TournamentMatch.tournament_id == tournament_id)
            .count()
        )
        completed_matches = (
            db.query(TournamentMatch)
            .filter(
                and_(
                    TournamentMatch.tournament_id == tournament_id,
                    TournamentMatch.status == MatchStatus.COMPLETED,
                )
            )
            .count()
        )

        total_teams = (
            db.query(TournamentTeam)
            .filter(TournamentTeam.tournament_id == tournament_id)
            .count()
        )

        total_participants = (
            db.query(TournamentParticipant)
            .filter(TournamentParticipant.tournament_id == tournament_id)
            .count()
        )

        categories_breakdown = {}
        for category_config in tournament.categories:
            team_count = (
                db.query(TournamentTeam)
                .filter(TournamentTeam.category_config_id == category_config.id)
                .count()
            )
            participant_count = (
                db.query(TournamentParticipant)
                .filter(TournamentParticipant.category_config_id == category_config.id)
                .count()
            )
            categories_breakdown[category_config.category.value] = {
                "teams": team_count,
                "participants": participant_count,
                "max_allowed": category_config.max_participants,
            }

        return {
            "tournament_id": tournament_id,
            "tournament_type": tournament.tournament_type.value,
            "total_matches": total_matches,
            "completed_matches": completed_matches,
            "pending_matches": total_matches - completed_matches,
            "total_teams": total_teams,
            "total_participants": total_participants,
            "categories_breakdown": categories_breakdown,
            "completion_percentage": (completed_matches / total_matches * 100)
            if total_matches > 0
            else 0,
        }

    def award_trophy(
        self,
        db: Session,
        tournament_id: int,
        category_config_id: int,
        user_id: int,
        team_id: int,
        position: int,
        trophy_type: str,
    ) -> TournamentTrophy:
        trophy = TournamentTrophy(
            tournament_id=tournament_id,
            category_config_id=category_config_id,
            user_id=user_id,
            team_id=team_id,
            position=position,
            trophy_type=trophy_type,
        )
        db.add(trophy)
        db.commit()
        db.refresh(trophy)
        return trophy

    def get_user_trophies(self, db: Session, user_id: int) -> list[TournamentTrophy]:
        return (
            db.query(TournamentTrophy)
            .options(
                joinedload(TournamentTrophy.tournament),
                joinedload(TournamentTrophy.category_config),
            )
            .filter(TournamentTrophy.user_id == user_id)
            .order_by(desc(TournamentTrophy.awarded_at))
            .all()
        )

    def debug_elo_eligibility(
        self, db: Session, user_elo: float, category: TournamentCategory
    ) -> dict[str, Any]:
        """Debug helper to check ELO eligibility for a specific category.

        Returns detailed information about why a user might not be eligible.
        """
        expected_range = CATEGORY_ELO_RANGES.get(category)
        if not expected_range:
            return {
                "eligible": False,
                "reason": f"Unknown category: {category}",
                "user_elo": user_elo,
                "category": category.value,
            }

        expected_min, expected_max = expected_range

        # Check all tournaments with this category
        tournaments_with_category = (
            db.query(Tournament)
            .join(TournamentCategoryConfig)
            .filter(TournamentCategoryConfig.category == category)
            .filter(Tournament.status == TournamentStatus.REGISTRATION_OPEN)
            .all()
        )

        eligible_tournaments = []
        ineligible_tournaments = []

        for tournament in tournaments_with_category:
            for category_config in tournament.categories:
                if category_config.category == category:
                    is_eligible = self._is_elo_eligible_for_category(
                        user_elo, category_config
                    )

                    tournament_info = {
                        "tournament_id": tournament.id,
                        "tournament_name": tournament.name,
                        "config_min_elo": category_config.min_elo,
                        "config_max_elo": category_config.max_elo,
                        "eligible": is_eligible,
                    }

                    if is_eligible:
                        eligible_tournaments.append(tournament_info)
                    else:
                        ineligible_tournaments.append(tournament_info)

        return {
            "user_elo": user_elo,
            "category": category.value,
            "expected_range": f"{expected_min}-{expected_max}",
            "total_open_tournaments": len(tournaments_with_category),
            "eligible_tournaments": eligible_tournaments,
            "ineligible_tournaments": ineligible_tournaments,
            "summary": {
                "can_join_any": len(eligible_tournaments) > 0,
                "total_eligible": len(eligible_tournaments),
                "total_ineligible": len(ineligible_tournaments),
            },
        }


tournament_crud = TournamentCRUD()
