from typing import Optional

from sqlalchemy.orm import Session

from app.models.game import Game
from app.models.game_player import GamePlayer as GamePlayerModel
from app.models.game_player import GamePlayerStatus, GamePlayerPosition, GamePlayerTeamSide


class GamePlayerCRUD:
    def get_game_player(
        self, db: Session, game_id: int, user_id: int
    ) -> Optional[GamePlayerModel]:
        """Retrieve a specific player in a game."""
        return (
            db.query(GamePlayerModel)
            .filter(
                GamePlayerModel.game_id == game_id, GamePlayerModel.user_id == user_id
            )
            .first()
        )

    def add_player_to_game(
        self,
        db: Session,
        game_id: int,
        user_id: int,
        status: GamePlayerStatus = GamePlayerStatus.INVITED,
    ) -> GamePlayerModel:
        """Add a player to a game with an initial status."""
        db_game_player = self.get_game_player(db, game_id=game_id, user_id=user_id)

        if not db_game_player:
            db_game_player = GamePlayerModel(
                game_id=game_id, user_id=user_id, status=status
            )
            db.add(db_game_player)
            db.commit()
            db.refresh(db_game_player)

        return db_game_player

    def update_game_player_status(
        self, db: Session, game_player: GamePlayerModel, status: GamePlayerStatus
    ) -> GamePlayerModel:
        """Update the status of a player in a game."""
        game_player.status = status
        db.add(game_player)
        db.commit()
        db.refresh(game_player)
        return game_player

    def get_players_for_game(self, db: Session, game_id: int) -> list[GamePlayerModel]:
        """Retrieve all players for a specific game."""
        return (
            db.query(GamePlayerModel).filter(GamePlayerModel.game_id == game_id).all()
        )

    def remove_player_from_game(self, db: Session, game_id: int, user_id: int) -> bool:
        """Remove a player from a game. Returns True if successful, False if
        player not found."""
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
            return {
                "can_leave": False,
                "reason": "Cannot leave a completed, cancelled, or expired game",
            }

        # Check 24-hour rule
        if not game.can_leave_game():
            return {
                "can_leave": False,
                "reason": "Cannot leave within 24 hours of game start time",
            }

        # Check if user is the game creator and only player
        is_creator = game.booking and game.booking.user_id == user_id
        accepted_players = [
            p for p in game.players if p.status == GamePlayerStatus.ACCEPTED
        ]

        if is_creator and len(accepted_players) == 1:
            return {
                "can_leave": False,
                "reason": (
                    "Game creator cannot leave when they are the only player. "
                    "Cancel the game instead."
                ),
            }

        return {"can_leave": True, "reason": ""}

    def update_player_position(
        self,
        db: Session,
        game_id: int,
        user_id: int,
        position: GamePlayerPosition,
        team_side: GamePlayerTeamSide
    ) -> Optional[GamePlayerModel]:
        """Update a player's position and team side in a game."""
        game_player = self.get_game_player(db, game_id, user_id)
        if not game_player:
            return None

        game_player.position = position
        game_player.team_side = team_side
        db.add(game_player)
        db.commit()
        db.refresh(game_player)
        return game_player

    def get_players_with_positions(self, db: Session, game_id: int) -> list[GamePlayerModel]:
        """Retrieve all players for a specific game with their positions."""
        return (
            db.query(GamePlayerModel)
            .filter(GamePlayerModel.game_id == game_id)
            .filter(GamePlayerModel.status == GamePlayerStatus.ACCEPTED)
            .all()
        )

    def validate_position_assignment(
        self,
        db: Session,
        game_id: int,
        user_id: int,
        position: GamePlayerPosition,
        team_side: GamePlayerTeamSide
    ) -> dict:
        """Validate if a position assignment is valid for a game."""
        # Get all accepted players with positions
        players = self.get_players_with_positions(db, game_id)

        # Check if the position is already taken on the same team
        for player in players:
            if (
                player.user_id != user_id and
                player.position == position and
                player.team_side == team_side
            ):
                return {
                    "valid": False,
                    "reason": f"Position {position.value} is already taken on {team_side.value}"
                }

        # Check if user is already assigned to a different team
        current_player = next((p for p in players if p.user_id == user_id), None)
        if current_player and current_player.team_side and current_player.team_side != team_side:
            return {
                "valid": False,
                "reason": f"Player is already assigned to {current_player.team_side.value}"
            }

        return {"valid": True, "reason": ""}

    def auto_assign_positions(self, db: Session, game_id: int) -> dict:
        """Auto-assign positions to players in a game."""
        # Get all accepted players without positions
        players = (
            db.query(GamePlayerModel)
            .filter(GamePlayerModel.game_id == game_id)
            .filter(GamePlayerModel.status == GamePlayerStatus.ACCEPTED)
            .all()
        )

        if len(players) != 4:
            return {
                "success": False,
                "reason": f"Need exactly 4 players for auto-assignment, found {len(players)}"
            }

        # Assign positions: first 2 players to TEAM_1, last 2 to TEAM_2
        assignments = [
            (players[0], GamePlayerPosition.LEFT, GamePlayerTeamSide.TEAM_1),
            (players[1], GamePlayerPosition.RIGHT, GamePlayerTeamSide.TEAM_1),
            (players[2], GamePlayerPosition.LEFT, GamePlayerTeamSide.TEAM_2),
            (players[3], GamePlayerPosition.RIGHT, GamePlayerTeamSide.TEAM_2),
        ]

        assigned_players = []
        for player, position, team_side in assignments:
            player.position = position
            player.team_side = team_side
            db.add(player)
            assigned_players.append(player)

        db.commit()

        # Refresh all players
        for player in assigned_players:
            db.refresh(player)

        return {
            "success": True,
            "assignments": [
                {
                    "user_id": player.user_id,
                    "position": player.position.value,
                    "team_side": player.team_side.value
                }
                for player in assigned_players
            ]
        }


# Create instance
game_player_crud = GamePlayerCRUD()
