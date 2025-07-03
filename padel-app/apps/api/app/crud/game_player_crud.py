from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.game_player import GamePlayer as GamePlayerModel, GamePlayerStatus
from app.models.game import Game


class GamePlayerCRUD:
    def get_game_player(self, db: Session, game_id: int, user_id: int) -> Optional[GamePlayerModel]:
        """Retrieve a specific player in a game."""
        return (
            db.query(GamePlayerModel)
            .filter(GamePlayerModel.game_id == game_id, GamePlayerModel.user_id == user_id)
            .first()
        )

    def add_player_to_game(
        self,
        db: Session, 
        game_id: int, 
        user_id: int, 
        status: GamePlayerStatus = GamePlayerStatus.INVITED
    ) -> GamePlayerModel:
        """Add a player to a game with an initial status."""
        db_game_player = self.get_game_player(db, game_id=game_id, user_id=user_id)
        
        if not db_game_player:
            db_game_player = GamePlayerModel(
                game_id=game_id,
                user_id=user_id,
                status=status
            )
            db.add(db_game_player)
            db.commit()
            db.refresh(db_game_player)
        
        return db_game_player

    def update_game_player_status(
        self,
        db: Session, 
        game_player: GamePlayerModel,
        status: GamePlayerStatus
    ) -> GamePlayerModel:
        """Update the status of a player in a game."""
        game_player.status = status
        db.add(game_player)
        db.commit()
        db.refresh(game_player)
        return game_player

    def get_players_for_game(self, db: Session, game_id: int) -> List[GamePlayerModel]:
        """Retrieve all players for a specific game."""
        return db.query(GamePlayerModel).filter(GamePlayerModel.game_id == game_id).all()
    
    def remove_player_from_game(self, db: Session, game_id: int, user_id: int) -> bool:
        """Remove a player from a game. Returns True if successful, False if player not found."""
        game_player = self.get_game_player(db, game_id, user_id)
        if game_player:
            db.delete(game_player)
            db.commit()
            return True
        return False
    
    def can_leave_game(self, db: Session, game_id: int, user_id: int) -> dict:
        """Check if a user can leave a game, considering timing restrictions."""
        game_player = self.get_game_player(db, game_id, user_id)
        if not game_player:
            return {"can_leave": False, "reason": "You are not part of this game"}
        
        game = db.query(Game).filter(Game.id == game_id).first()
        if not game:
            return {"can_leave": False, "reason": "Game not found"}
        
        # Check if game is completed or cancelled
        if game.game_status in ["COMPLETED", "CANCELLED", "EXPIRED"]:
            return {"can_leave": False, "reason": "Cannot leave a completed, cancelled, or expired game"}
        
        # Check 24-hour rule
        if not game.can_leave_game():
            return {"can_leave": False, "reason": "Cannot leave within 24 hours of game start time"}
        
        # Check if user is the game creator and only player
        is_creator = game.booking and game.booking.user_id == user_id
        accepted_players = [p for p in game.players if p.status == GamePlayerStatus.ACCEPTED]
        
        if is_creator and len(accepted_players) == 1:
            return {"can_leave": False, "reason": "Game creator cannot leave when they are the only player. Cancel the game instead."}
        
        return {"can_leave": True, "reason": ""}


# Create instance
game_player_crud = GamePlayerCRUD()