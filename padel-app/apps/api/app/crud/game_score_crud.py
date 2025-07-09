from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session, joinedload

from app.models import Game, GameScore, ScoreConfirmation
from app.models.game_score import ConfirmationAction, ScoreStatus
from app.schemas.game_score_schemas import GameScoreCreate, ScoreConfirmationCreate


class GameScoreCRUD:
    """CRUD operations for game scores and confirmations"""

    def create_game_score(
        self,
        db: Session,
        score_data: GameScoreCreate,
        submitted_by_user_id: int,
    ) -> GameScore:
        """Create a new game score submission"""
        game_score = GameScore(
            game_id=score_data.game_id,
            team1_score=score_data.team1_score,
            team2_score=score_data.team2_score,
            submitted_by_team=score_data.submitted_by_team,
            submitted_by_user_id=submitted_by_user_id,
            status=ScoreStatus.PENDING,
        )

        db.add(game_score)
        db.commit()
        db.refresh(game_score)
        return game_score

    def get_game_score(self, db: Session, score_id: int) -> Optional[GameScore]:
        """Get a game score by ID with related data"""
        return (
            db.query(GameScore)
            .filter(GameScore.id == score_id)
            .options(
                joinedload(GameScore.game),
                joinedload(GameScore.submitted_by),
                joinedload(GameScore.confirmations),
            )
            .first()
        )

    def get_game_scores_by_game(self, db: Session, game_id: int) -> list[GameScore]:
        """Get all score submissions for a game"""
        return (
            db.query(GameScore)
            .filter(GameScore.game_id == game_id)
            .options(
                joinedload(GameScore.submitted_by),
                joinedload(GameScore.confirmations),
            )
            .order_by(GameScore.submitted_at.desc())
            .all()
        )

    def get_latest_game_score(self, db: Session, game_id: int) -> Optional[GameScore]:
        """Get the most recent score submission for a game"""
        return (
            db.query(GameScore)
            .filter(GameScore.game_id == game_id)
            .options(
                joinedload(GameScore.submitted_by),
                joinedload(GameScore.confirmations),
            )
            .order_by(GameScore.submitted_at.desc())
            .first()
        )

    def create_score_confirmation(
        self,
        db: Session,
        confirmation_data: ScoreConfirmationCreate,
        confirming_user_id: int,
    ) -> ScoreConfirmation:
        """Create a score confirmation or counter"""
        confirmation = ScoreConfirmation(
            game_score_id=confirmation_data.game_score_id,
            confirming_team=confirmation_data.confirming_team,
            confirming_user_id=confirming_user_id,
            action=confirmation_data.action,
            counter_team1_score=confirmation_data.counter_team1_score,
            counter_team2_score=confirmation_data.counter_team2_score,
            counter_notes=confirmation_data.counter_notes,
        )

        db.add(confirmation)
        db.commit()
        db.refresh(confirmation)
        return confirmation

    def confirm_score(
        self, db: Session, score_id: int, confirming_team: int, confirming_user_id: int
    ) -> Optional[GameScore]:
        """Confirm a score submission"""
        game_score = self.get_game_score(db, score_id)
        if not game_score:
            return None

        # Check if already confirmed by this team
        existing_confirmation = (
            db.query(ScoreConfirmation)
            .filter(
                ScoreConfirmation.game_score_id == score_id,
                ScoreConfirmation.confirming_team == confirming_team,
                ScoreConfirmation.action == ConfirmationAction.CONFIRM,
            )
            .first()
        )

        if existing_confirmation:
            return game_score  # Already confirmed

        # Create confirmation
        confirmation = ScoreConfirmation(
            game_score_id=score_id,
            confirming_team=confirming_team,
            confirming_user_id=confirming_user_id,
            action=ConfirmationAction.CONFIRM,
        )

        db.add(confirmation)

        # Check if both teams have now confirmed
        confirmations = (
            db.query(ScoreConfirmation)
            .filter(
                ScoreConfirmation.game_score_id == score_id,
                ScoreConfirmation.action == ConfirmationAction.CONFIRM,
            )
            .all()
        )

        # Count unique teams that have confirmed
        confirmed_teams = {conf.confirming_team for conf in confirmations}
        confirmed_teams.add(confirming_team)  # Add the current confirmation

        if len(confirmed_teams) >= 2:
            # Both teams confirmed - finalize the score
            game_score.status = ScoreStatus.CONFIRMED
            game_score.final_team1_score = game_score.team1_score
            game_score.final_team2_score = game_score.team2_score
            game_score.confirmed_at = datetime.now(timezone.utc)

            # Update the game's result
            self._update_game_result(db, game_score)

        db.commit()
        db.refresh(game_score)
        return game_score

    def counter_score(
        self,
        db: Session,
        score_id: int,
        confirming_team: int,
        confirming_user_id: int,
        counter_team1_score: int,
        counter_team2_score: int,
        counter_notes: Optional[str] = None,
    ) -> Optional[GameScore]:
        """Counter/dispute a score submission"""
        game_score = self.get_game_score(db, score_id)
        if not game_score:
            return None

        # Create counter confirmation
        confirmation = ScoreConfirmation(
            game_score_id=score_id,
            confirming_team=confirming_team,
            confirming_user_id=confirming_user_id,
            action=ConfirmationAction.COUNTER,
            counter_team1_score=counter_team1_score,
            counter_team2_score=counter_team2_score,
            counter_notes=counter_notes,
        )

        db.add(confirmation)

        # Mark score as disputed
        game_score.status = ScoreStatus.DISPUTED

        db.commit()
        db.refresh(game_score)
        return game_score

    def resolve_disputed_score(
        self,
        db: Session,
        score_id: int,
        final_team1_score: int,
        final_team2_score: int,
        admin_notes: Optional[str] = None,
    ) -> Optional[GameScore]:
        """Admin resolution of a disputed score"""
        game_score = self.get_game_score(db, score_id)
        if not game_score:
            return None

        game_score.status = ScoreStatus.RESOLVED
        game_score.final_team1_score = final_team1_score
        game_score.final_team2_score = final_team2_score
        game_score.confirmed_at = datetime.now(timezone.utc)
        game_score.admin_resolved = True
        game_score.admin_notes = admin_notes

        # Update the game's result
        self._update_game_result(db, game_score)

        db.commit()
        db.refresh(game_score)
        return game_score

    def can_submit_score(
        self, db: Session, game_id: int, user_id: int
    ) -> tuple[bool, str]:
        """Check if a user can submit a score for a game"""
        game = db.query(Game).filter(Game.id == game_id).first()
        if not game:
            return False, "Game not found"

        # Check if game has ended
        current_time = datetime.now(timezone.utc)
        # Handle timezone-naive end_time
        if game.end_time.tzinfo is None:
            end_time_aware = game.end_time.replace(tzinfo=timezone.utc)
            if current_time < end_time_aware:
                return False, "Cannot submit score before game ends"
        elif current_time < game.end_time:
            return False, "Cannot submit score before game ends"

        # Check if user is part of the game
        user_in_game = any(
            gp.user_id == user_id and gp.status.value == "ACCEPTED"
            for gp in game.players
        )
        if not user_in_game:
            return False, "You are not a participant in this game"

        # Check if teams are assigned (required for score submission)
        if not game.team1_id or not game.team2_id:
            return False, "Teams have not been assigned for this game yet"

        # Check if score already confirmed
        latest_score = self.get_latest_game_score(db, game_id)
        if latest_score and latest_score.status in [
            ScoreStatus.CONFIRMED,
            ScoreStatus.RESOLVED,
        ]:
            return False, "Score has already been confirmed for this game"

        return True, "Can submit score"

    def can_confirm_score(
        self, db: Session, score_id: int, user_id: int
    ) -> tuple[bool, str]:
        """Check if a user can confirm a score"""
        game_score = self.get_game_score(db, score_id)
        if not game_score:
            return False, "Score not found"

        if game_score.status != ScoreStatus.PENDING:
            return (
                False,
                f"Score is not pending confirmation (status: {game_score.status})",
            )

        # Check if user is part of the game
        game = game_score.game
        user_in_game = any(
            gp.user_id == user_id and gp.status.value == "ACCEPTED"
            for gp in game.players
        )
        if not user_in_game:
            return False, "You are not a participant in this game"

        # Check if user submitted the score (can't confirm own submission)
        if game_score.submitted_by_user_id == user_id:
            return False, "Cannot confirm your own score submission"

        return True, "Can confirm score"

    def get_user_team_for_game(
        self, db: Session, game_id: int, user_id: int
    ) -> Optional[int]:
        """Get which team (1 or 2) a user belongs to in a game"""
        game = (
            db.query(Game)
            .filter(Game.id == game_id)
            .options(
                joinedload(Game.team1).joinedload("players"),
                joinedload(Game.team2).joinedload("players"),
                joinedload(Game.players),
            )
            .first()
        )
        if not game:
            return None

        # Check team1
        if game.team1:
            for player in game.team1.players:
                if player.id == user_id:
                    return 1

        # Check team2
        if game.team2:
            for player in game.team2.players:
                if player.id == user_id:
                    return 2

        # For games without teams assigned yet (future games),
        # check if user is a participant
        user_in_game = any(
            gp.user_id == user_id and gp.status.value == "ACCEPTED"
            for gp in game.players
        )
        if user_in_game:
            # Return a placeholder team number for participants
            # This allows them to view score history but not submit scores
            return -1

        return None

    def _update_game_result(self, db: Session, game_score: GameScore):
        """Update the game's winning team based on confirmed score"""
        winning_team_number = game_score.get_winning_team()
        if winning_team_number == 0:
            return  # Tie, no winner

        game = game_score.game
        if winning_team_number == 1:
            game.winning_team_id = game.team1_id
        elif winning_team_number == 2:
            game.winning_team_id = game.team2_id

        game.result_submitted = True
        db.add(game)


# Global CRUD instance
game_score_crud = GameScoreCRUD()
