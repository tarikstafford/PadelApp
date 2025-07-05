from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.crud.game_crud import game_crud
from app.models.game import Game, GameStatus


class GameExpirationService:
    def expire_past_games(self, db: Session) -> list[int]:
        """
        Find and expire games that are past their end time.
        Returns list of expired game IDs.
        """
        expired_game_ids = []

        # Find all scheduled games that are past their end time
        past_games = (
            db.query(Game)
            .filter(
                Game.game_status == GameStatus.SCHEDULED,
                Game.end_time < datetime.now(timezone.utc),
            )
            .all()
        )

        for game in past_games:
            game.game_status = GameStatus.EXPIRED
            db.add(game)
            expired_game_ids.append(game.id)

        db.commit()
        return expired_game_ids

    def check_single_game_expiration(self, db: Session, game_id: int) -> bool:
        """
        Check and expire a single game if needed.
        Returns True if game was expired, False otherwise.
        """
        game = game_crud.get_game(db, game_id)
        if not game:
            return False

        if game.should_auto_expire():
            game.game_status = GameStatus.EXPIRED
            db.add(game)
            db.commit()
            return True

        return False


# Create instance
game_expiration_service = GameExpirationService()
