from datetime import datetime, timezone
from typing import List, Dict, Any

from sqlalchemy.orm import Session
import logging

from app.models.tournament import Tournament, TournamentStatus

logger = logging.getLogger(__name__)


class TournamentExpirationService:
    """
    Service to handle automatic tournament expiration based on dates.
    """

    def expire_past_tournaments(self, db: Session) -> Dict[str, Any]:
        """
        Find and expire tournaments that are past their registration deadlines or end dates.
        
        Transitions:
        - REGISTRATION_OPEN → REGISTRATION_CLOSED (if registration_deadline has passed)
        - REGISTRATION_CLOSED → COMPLETED (if end_date has passed and no matches in progress)
        - IN_PROGRESS → COMPLETED (if end_date has passed)
        
        Returns summary of expired tournaments.
        """
        current_time = datetime.now(timezone.utc)
        
        # Track changes
        registration_closed_count = 0
        completed_count = 0
        registration_closed_ids = []
        completed_ids = []
        
        try:
            # 1. Close registration for tournaments past their deadline
            tournaments_to_close_registration = (
                db.query(Tournament)
                .filter(
                    Tournament.status == TournamentStatus.REGISTRATION_OPEN,
                    Tournament.registration_deadline < current_time,
                )
                .all()
            )
            
            for tournament in tournaments_to_close_registration:
                logger.info(f"Closing registration for tournament {tournament.id}: {tournament.name}")
                tournament.status = TournamentStatus.REGISTRATION_CLOSED
                db.add(tournament)
                registration_closed_count += 1
                registration_closed_ids.append(tournament.id)
            
            # 2. Complete tournaments that are past their end date
            tournaments_to_complete = (
                db.query(Tournament)
                .filter(
                    Tournament.status.in_([
                        TournamentStatus.REGISTRATION_CLOSED,
                        TournamentStatus.IN_PROGRESS
                    ]),
                    Tournament.end_date < current_time,
                )
                .all()
            )
            
            for tournament in tournaments_to_complete:
                # Check if tournament has any unfinished matches
                if self._has_unfinished_matches(db, tournament.id):
                    logger.warning(f"Tournament {tournament.id} has unfinished matches, keeping status as IN_PROGRESS")
                    if tournament.status != TournamentStatus.IN_PROGRESS:
                        tournament.status = TournamentStatus.IN_PROGRESS
                        db.add(tournament)
                else:
                    logger.info(f"Completing tournament {tournament.id}: {tournament.name}")
                    tournament.status = TournamentStatus.COMPLETED
                    db.add(tournament)
                    completed_count += 1
                    completed_ids.append(tournament.id)
            
            # Commit all changes
            db.commit()
            
            logger.info(f"Tournament expiration completed: {registration_closed_count} registrations closed, {completed_count} tournaments completed")
            
            return {
                "success": True,
                "registration_closed_count": registration_closed_count,
                "completed_count": completed_count,
                "registration_closed_ids": registration_closed_ids,
                "completed_ids": completed_ids,
                "total_processed": registration_closed_count + completed_count,
                "timestamp": current_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error during tournament expiration: {e}")
            db.rollback()
            return {
                "success": False,
                "error": str(e),
                "registration_closed_count": 0,
                "completed_count": 0,
                "registration_closed_ids": [],
                "completed_ids": [],
                "total_processed": 0,
                "timestamp": current_time.isoformat()
            }
    
    def check_single_tournament_expiration(self, db: Session, tournament_id: int) -> Dict[str, Any]:
        """
        Check and expire a single tournament if needed.
        
        Returns dict with expiration status and actions taken.
        """
        current_time = datetime.now(timezone.utc)
        
        try:
            tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
            
            if not tournament:
                return {
                    "success": False,
                    "error": "Tournament not found",
                    "action_taken": None
                }
            
            original_status = tournament.status
            action_taken = None
            
            # Check if registration should be closed
            if (tournament.status == TournamentStatus.REGISTRATION_OPEN and 
                tournament.registration_deadline < current_time):
                
                tournament.status = TournamentStatus.REGISTRATION_CLOSED
                action_taken = "registration_closed"
                logger.info(f"Closed registration for tournament {tournament.id}")
            
            # Check if tournament should be completed
            elif (tournament.status in [TournamentStatus.REGISTRATION_CLOSED, TournamentStatus.IN_PROGRESS] and 
                  tournament.end_date < current_time):
                
                if self._has_unfinished_matches(db, tournament.id):
                    if tournament.status != TournamentStatus.IN_PROGRESS:
                        tournament.status = TournamentStatus.IN_PROGRESS
                        action_taken = "marked_in_progress"
                        logger.info(f"Marked tournament {tournament.id} as IN_PROGRESS due to unfinished matches")
                else:
                    tournament.status = TournamentStatus.COMPLETED
                    action_taken = "completed"
                    logger.info(f"Completed tournament {tournament.id}")
            
            # Save changes if status changed
            if tournament.status != original_status:
                db.add(tournament)
                db.commit()
            
            return {
                "success": True,
                "tournament_id": tournament.id,
                "original_status": original_status.value,
                "new_status": tournament.status.value,
                "action_taken": action_taken,
                "timestamp": current_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error checking tournament {tournament_id} expiration: {e}")
            db.rollback()
            return {
                "success": False,
                "error": str(e),
                "tournament_id": tournament_id,
                "action_taken": None
            }
    
    def _has_unfinished_matches(self, db: Session, tournament_id: int) -> bool:
        """
        Check if a tournament has any unfinished matches.
        Returns True if there are matches that are not completed.
        """
        try:
            from app.models.tournament import TournamentMatch, MatchStatus
            
            unfinished_matches = (
                db.query(TournamentMatch)
                .filter(
                    TournamentMatch.tournament_id == tournament_id,
                    TournamentMatch.status.in_([
                        MatchStatus.SCHEDULED,
                        MatchStatus.IN_PROGRESS
                    ])
                )
                .count()
            )
            
            return unfinished_matches > 0
            
        except Exception as e:
            logger.error(f"Error checking unfinished matches for tournament {tournament_id}: {e}")
            return False
    
    def get_tournaments_needing_expiration(self, db: Session) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get a summary of tournaments that need expiration without actually expiring them.
        Useful for monitoring and reporting.
        """
        current_time = datetime.now(timezone.utc)
        
        try:
            # Find tournaments that need registration closed
            registration_to_close = (
                db.query(Tournament)
                .filter(
                    Tournament.status == TournamentStatus.REGISTRATION_OPEN,
                    Tournament.registration_deadline < current_time,
                )
                .all()
            )
            
            # Find tournaments that need completion
            tournaments_to_complete = (
                db.query(Tournament)
                .filter(
                    Tournament.status.in_([
                        TournamentStatus.REGISTRATION_CLOSED,
                        TournamentStatus.IN_PROGRESS
                    ]),
                    Tournament.end_date < current_time,
                )
                .all()
            )
            
            registration_list = []
            for tournament in registration_to_close:
                registration_list.append({
                    "id": tournament.id,
                    "name": tournament.name,
                    "status": tournament.status.value,
                    "registration_deadline": tournament.registration_deadline.isoformat(),
                    "club_id": tournament.club_id
                })
            
            completion_list = []
            for tournament in tournaments_to_complete:
                completion_list.append({
                    "id": tournament.id,
                    "name": tournament.name,
                    "status": tournament.status.value,
                    "end_date": tournament.end_date.isoformat(),
                    "club_id": tournament.club_id,
                    "has_unfinished_matches": self._has_unfinished_matches(db, tournament.id)
                })
            
            return {
                "registration_to_close": registration_list,
                "tournaments_to_complete": completion_list,
                "total_needing_action": len(registration_list) + len(completion_list),
                "timestamp": current_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting tournaments needing expiration: {e}")
            return {
                "error": str(e),
                "registration_to_close": [],
                "tournaments_to_complete": [],
                "total_needing_action": 0,
                "timestamp": current_time.isoformat()
            }


# Create instance
tournament_expiration_service = TournamentExpirationService()