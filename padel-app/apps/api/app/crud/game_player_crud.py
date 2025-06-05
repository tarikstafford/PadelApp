from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.game_player import GamePlayer as GamePlayerModel, GamePlayerStatus
# from app.schemas.game_schemas import GamePlayerCreate # Schemas typically used at router level

def get_game_player(db: Session, game_id: int, user_id: int) -> Optional[GamePlayerModel]:
    """Retrieve a specific player in a game."""
    return (
        db.query(GamePlayerModel)
        .filter(GamePlayerModel.game_id == game_id, GamePlayerModel.user_id == user_id)
        .first()
    )

def add_player_to_game(
    db: Session, 
    game_id: int, 
    user_id: int, 
    status: GamePlayerStatus = GamePlayerStatus.INVITED
) -> GamePlayerModel:
    """Add a player to a game with an initial status."""
    # Check if player is already in the game to avoid duplicates, or handle as an update
    db_game_player = get_game_player(db, game_id=game_id, user_id=user_id)
    if db_game_player:
        # Potentially update status or raise an error, depending on desired logic
        # For now, let's assume we don't re-add if already exists with any status.
        # Or, if re-inviting, perhaps update status to INVITED if currently DECLINED.
        # This logic might be better placed in a service layer or router for invitations.
        # For this basic CRUD, we'll just return the existing one or one could raise error.
        # Let's modify to create if not exists, or update if exists (more robust for invites later)
        # For simplicity now, let's assume this is called when we know the player isn't there or it's a fresh add.
        # A more complete version would be in the invitation service/router.
        # Current subtask is mostly about game creation, creator is first player.
        pass # Fall through to create if not found, this check is more for invite logic

    # If strictly for adding new, the check above would raise an error or return existing.
    # If we want to ensure only one entry, the get_game_player should be used by caller first.
    
    # For this version, let's assume the caller ensures no duplicates before calling directly for adding.
    # Or, for a game creator, they are added once.
    if not db_game_player: # Only create if not existing at all
        db_game_player = GamePlayerModel(
            game_id=game_id,
            user_id=user_id,
            status=status
        )
        db.add(db_game_player)
        db.commit()
        db.refresh(db_game_player)
        return db_game_player
    return db_game_player # Return existing if found by the simple check

def update_game_player_status(
    db: Session, 
    game_player: GamePlayerModel, # Expects the ORM model instance
    status: GamePlayerStatus
) -> GamePlayerModel:
    """Update the status of a player in a game."""
    game_player.status = status
    db.add(game_player) # Add to session to track changes
    db.commit()
    db.refresh(game_player)
    return game_player

def get_players_for_game(db: Session, game_id: int) -> List[GamePlayerModel]:
    """Retrieve all players for a specific game."""
    return db.query(GamePlayerModel).filter(GamePlayerModel.game_id == game_id).all() 