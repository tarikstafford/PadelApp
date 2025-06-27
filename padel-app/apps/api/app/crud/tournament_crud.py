from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, asc, func
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.models.tournament import (
    Tournament, TournamentStatus, TournamentType, TournamentCategory,
    TournamentCategoryConfig, TournamentTeam, TournamentMatch, MatchStatus,
    TournamentCourtBooking, TournamentTrophy, CATEGORY_ELO_RANGES
)
from app.models.team import Team
from app.models.user import User
from app.models.court import Court
from app.schemas.tournament_schemas import (
    TournamentCreate, TournamentUpdate, TournamentCategoryCreate,
    TournamentTeamCreate, TournamentMatchCreate, TournamentMatchUpdate
)

class TournamentCRUD:
    def create_tournament(self, db: Session, tournament_data: TournamentCreate, club_id: int) -> Tournament:
        # Create tournament
        tournament = Tournament(
            club_id=club_id,
            name=tournament_data.name,
            description=tournament_data.description,
            tournament_type=tournament_data.tournament_type,
            start_date=tournament_data.start_date,
            end_date=tournament_data.end_date,
            registration_deadline=tournament_data.registration_deadline,
            max_participants=tournament_data.max_participants,
            entry_fee=tournament_data.entry_fee or 0.0,
            status=TournamentStatus.DRAFT
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
                max_elo=elo_range[1]
            )
            db.add(category_config)

        # Block courts for tournament dates
        for court_id in tournament_data.court_ids:
            court_booking = TournamentCourtBooking(
                tournament_id=tournament.id,
                court_id=court_id,
                start_time=tournament_data.start_date,
                end_time=tournament_data.end_date
            )
            db.add(court_booking)

        db.commit()
        db.refresh(tournament)
        return tournament

    def get_tournament(self, db: Session, tournament_id: int) -> Optional[Tournament]:
        return db.query(Tournament).options(
            joinedload(Tournament.categories),
            joinedload(Tournament.teams).joinedload(TournamentTeam.team),
            joinedload(Tournament.matches),
            joinedload(Tournament.court_bookings)
        ).filter(Tournament.id == tournament_id).first()

    def get_tournaments_by_club(self, db: Session, club_id: int, skip: int = 0, limit: int = 100) -> List[Tournament]:
        return db.query(Tournament).filter(Tournament.club_id == club_id).offset(skip).limit(limit).all()

    def get_tournaments_by_status(self, db: Session, status: TournamentStatus, skip: int = 0, limit: int = 100) -> List[Tournament]:
        return db.query(Tournament).filter(Tournament.status == status).offset(skip).limit(limit).all()

    def update_tournament(self, db: Session, tournament_id: int, tournament_data: TournamentUpdate) -> Optional[Tournament]:
        tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
        if not tournament:
            return None

        update_data = tournament_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(tournament, field, value)

        tournament.updated_at = datetime.utcnow()
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

    def register_team(self, db: Session, tournament_id: int, team_data: TournamentTeamCreate) -> Optional[TournamentTeam]:
        # Check tournament exists and is open for registration
        tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
        if not tournament or tournament.status != TournamentStatus.REGISTRATION_OPEN:
            return None

        # Get category config
        category_config = db.query(TournamentCategoryConfig).filter(
            and_(
                TournamentCategoryConfig.tournament_id == tournament_id,
                TournamentCategoryConfig.category == team_data.category
            )
        ).first()
        if not category_config:
            return None

        # Check if team is already registered
        existing_registration = db.query(TournamentTeam).filter(
            and_(
                TournamentTeam.tournament_id == tournament_id,
                TournamentTeam.team_id == team_data.team_id
            )
        ).first()
        if existing_registration:
            return None

        # Get team and calculate average ELO
        team = db.query(Team).options(joinedload(Team.players)).filter(Team.id == team_data.team_id).first()
        if not team or len(team.players) != 2:  # Padel teams must have exactly 2 players
            return None

        average_elo = sum(player.elo_rating for player in team.players) / len(team.players)

        # Check ELO eligibility
        if not (category_config.min_elo <= average_elo < category_config.max_elo):
            return None

        # Check category capacity
        current_teams = db.query(TournamentTeam).filter(
            TournamentTeam.category_config_id == category_config.id
        ).count()
        if current_teams >= category_config.max_participants:
            return None

        # Register team
        tournament_team = TournamentTeam(
            tournament_id=tournament_id,
            category_config_id=category_config.id,
            team_id=team_data.team_id,
            average_elo=average_elo
        )
        db.add(tournament_team)
        db.commit()
        db.refresh(tournament_team)
        return tournament_team

    def unregister_team(self, db: Session, tournament_id: int, team_id: int) -> bool:
        tournament_team = db.query(TournamentTeam).filter(
            and_(
                TournamentTeam.tournament_id == tournament_id,
                TournamentTeam.team_id == team_id
            )
        ).first()
        if not tournament_team:
            return False

        db.delete(tournament_team)
        db.commit()
        return True

    def get_tournament_teams(self, db: Session, tournament_id: int, category: Optional[TournamentCategory] = None) -> List[TournamentTeam]:
        query = db.query(TournamentTeam).options(
            joinedload(TournamentTeam.team).joinedload(Team.players),
            joinedload(TournamentTeam.category_config)
        ).filter(TournamentTeam.tournament_id == tournament_id)
        
        if category:
            query = query.join(TournamentCategoryConfig).filter(TournamentCategoryConfig.category == category)
        
        return query.all()

    def create_match(self, db: Session, tournament_id: int, category_config_id: int, match_data: TournamentMatchCreate) -> TournamentMatch:
        match = TournamentMatch(
            tournament_id=tournament_id,
            category_config_id=category_config_id,
            team1_id=match_data.team1_id,
            team2_id=match_data.team2_id,
            round_number=match_data.round_number,
            match_number=match_data.match_number,
            scheduled_time=match_data.scheduled_time,
            court_id=match_data.court_id
        )
        db.add(match)
        db.commit()
        db.refresh(match)
        return match

    def update_match(self, db: Session, match_id: int, match_data: TournamentMatchUpdate) -> Optional[TournamentMatch]:
        match = db.query(TournamentMatch).filter(TournamentMatch.id == match_id).first()
        if not match:
            return None

        update_data = match_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(match, field, value)

        match.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(match)
        return match

    def get_tournament_matches(self, db: Session, tournament_id: int, category: Optional[TournamentCategory] = None) -> List[TournamentMatch]:
        query = db.query(TournamentMatch).options(
            joinedload(TournamentMatch.team1).joinedload(TournamentTeam.team),
            joinedload(TournamentMatch.team2).joinedload(TournamentTeam.team),
            joinedload(TournamentMatch.court),
            joinedload(TournamentMatch.category_config)
        ).filter(TournamentMatch.tournament_id == tournament_id)
        
        if category:
            query = query.join(TournamentCategoryConfig).filter(TournamentCategoryConfig.category == category)
        
        return query.order_by(TournamentMatch.round_number, TournamentMatch.match_number).all()

    def get_match(self, db: Session, match_id: int) -> Optional[TournamentMatch]:
        return db.query(TournamentMatch).options(
            joinedload(TournamentMatch.team1).joinedload(TournamentTeam.team),
            joinedload(TournamentMatch.team2).joinedload(TournamentTeam.team),
            joinedload(TournamentMatch.court)
        ).filter(TournamentMatch.id == match_id).first()

    def get_upcoming_matches(self, db: Session, club_id: int, limit: int = 10) -> List[TournamentMatch]:
        return db.query(TournamentMatch).join(Tournament).filter(
            and_(
                Tournament.club_id == club_id,
                TournamentMatch.scheduled_time > datetime.utcnow(),
                TournamentMatch.status == MatchStatus.SCHEDULED
            )
        ).order_by(TournamentMatch.scheduled_time).limit(limit).all()

    def check_team_eligibility(self, db: Session, tournament_id: int, team_id: int) -> Dict[str, Any]:
        tournament = db.query(Tournament).options(joinedload(Tournament.categories)).filter(Tournament.id == tournament_id).first()
        if not tournament:
            return {"eligible": False, "reason": "Tournament not found"}

        team = db.query(Team).options(joinedload(Team.players)).filter(Team.id == team_id).first()
        if not team:
            return {"eligible": False, "reason": "Team not found"}

        if len(team.players) != 2:
            return {"eligible": False, "reason": "Team must have exactly 2 players"}

        average_elo = sum(player.elo_rating for player in team.players) / len(team.players)
        eligible_categories = []
        
        for category_config in tournament.categories:
            if category_config.min_elo <= average_elo < category_config.max_elo:
                # Check capacity
                current_teams = db.query(TournamentTeam).filter(
                    TournamentTeam.category_config_id == category_config.id
                ).count()
                if current_teams < category_config.max_participants:
                    eligible_categories.append(category_config.category)

        return {
            "eligible": len(eligible_categories) > 0,
            "eligible_categories": eligible_categories,
            "average_elo": average_elo,
            "team_players": [{"id": p.id, "name": p.full_name, "elo": p.elo_rating} for p in team.players]
        }

    def get_tournament_stats(self, db: Session, tournament_id: int) -> Optional[Dict[str, Any]]:
        tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
        if not tournament:
            return None

        total_matches = db.query(TournamentMatch).filter(TournamentMatch.tournament_id == tournament_id).count()
        completed_matches = db.query(TournamentMatch).filter(
            and_(
                TournamentMatch.tournament_id == tournament_id,
                TournamentMatch.status == MatchStatus.COMPLETED
            )
        ).count()
        
        total_teams = db.query(TournamentTeam).filter(TournamentTeam.tournament_id == tournament_id).count()
        
        categories_breakdown = {}
        for category_config in tournament.categories:
            team_count = db.query(TournamentTeam).filter(
                TournamentTeam.category_config_id == category_config.id
            ).count()
            categories_breakdown[category_config.category.value] = team_count

        return {
            "tournament_id": tournament_id,
            "total_matches": total_matches,
            "completed_matches": completed_matches,
            "pending_matches": total_matches - completed_matches,
            "total_teams": total_teams,
            "categories_breakdown": categories_breakdown,
            "completion_percentage": (completed_matches / total_matches * 100) if total_matches > 0 else 0
        }

    def award_trophy(self, db: Session, tournament_id: int, category_config_id: int, user_id: int, team_id: int, position: int, trophy_type: str) -> TournamentTrophy:
        trophy = TournamentTrophy(
            tournament_id=tournament_id,
            category_config_id=category_config_id,
            user_id=user_id,
            team_id=team_id,
            position=position,
            trophy_type=trophy_type
        )
        db.add(trophy)
        db.commit()
        db.refresh(trophy)
        return trophy

    def get_user_trophies(self, db: Session, user_id: int) -> List[TournamentTrophy]:
        return db.query(TournamentTrophy).options(
            joinedload(TournamentTrophy.tournament),
            joinedload(TournamentTrophy.category_config)
        ).filter(TournamentTrophy.user_id == user_id).order_by(desc(TournamentTrophy.awarded_at)).all()

tournament_crud = TournamentCRUD()