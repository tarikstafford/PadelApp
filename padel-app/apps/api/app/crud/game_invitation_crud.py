from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.game_invitation import GameInvitation
from app.models.game import Game
from app.models.user import User
from app.models.game_player import GamePlayer, GamePlayerStatus
from app.schemas.game_invitation_schemas import GameInvitationCreate

class GameInvitationCRUD:
    def create_invitation(self, db: Session, game_id: int, created_by: int, expires_in_hours: int = 24, max_uses: Optional[int] = None) -> GameInvitation:
        """Create a new game invitation"""
        invitation = GameInvitation.create_invitation(
            game_id=game_id,
            created_by=created_by,
            expires_in_hours=expires_in_hours,
            max_uses=max_uses
        )
        db.add(invitation)
        db.commit()
        db.refresh(invitation)
        return invitation

    def get_invitation_by_token(self, db: Session, token: str) -> Optional[GameInvitation]:
        """Get invitation by token"""
        return db.query(GameInvitation).filter(GameInvitation.token == token).first()

    def get_invitations_for_game(self, db: Session, game_id: int) -> List[GameInvitation]:
        """Get all invitations for a specific game"""
        return db.query(GameInvitation).filter(GameInvitation.game_id == game_id).all()

    def deactivate_invitation(self, db: Session, invitation_id: int) -> bool:
        """Deactivate an invitation"""
        invitation = db.query(GameInvitation).filter(GameInvitation.id == invitation_id).first()
        if invitation:
            invitation.is_active = False
            db.commit()
            return True
        return False

    def accept_invitation(self, db: Session, token: str, user_id: int) -> dict:
        """Accept a game invitation and add user to game"""
        invitation = self.get_invitation_by_token(db, token)
        
        if not invitation:
            return {"success": False, "message": "Invitation not found"}
        
        if not invitation.is_valid():
            return {"success": False, "message": "Invitation has expired or is no longer valid"}
        
        # Check if user is already in the game
        existing_player = db.query(GamePlayer).filter(
            and_(
                GamePlayer.game_id == invitation.game_id,
                GamePlayer.user_id == user_id
            )
        ).first()
        
        if existing_player:
            return {"success": False, "message": "You are already part of this game"}
        
        # Check if game is full
        game = db.query(Game).filter(Game.id == invitation.game_id).first()
        if not game:
            return {"success": False, "message": "Game not found"}
        
        current_players_count = db.query(GamePlayer).filter(
            and_(
                GamePlayer.game_id == invitation.game_id,
                GamePlayer.status == GamePlayerStatus.ACCEPTED
            )
        ).count()
        
        if current_players_count >= 4:  # Max players per game
            return {"success": False, "message": "Game is full"}
        
        # Add user to game
        from app.crud.game_player_crud import game_player_crud
        game_player = game_player_crud.add_player_to_game(
            db=db,
            game_id=invitation.game_id,
            user_id=user_id,
            status=GamePlayerStatus.ACCEPTED
        )
        
        # Increment invitation usage
        invitation.increment_usage()
        db.commit()
        
        return {
            "success": True,
            "message": "Successfully joined the game!",
            "game_id": invitation.game_id,
            "game_player": game_player
        }

    def get_invitation_info(self, db: Session, token: str) -> Optional[dict]:
        """Get public information about an invitation (for preview before auth)"""
        invitation = self.get_invitation_by_token(db, token)
        
        if not invitation:
            return None
        
        game = db.query(Game).filter(Game.id == invitation.game_id).first()
        if not game:
            return None
        
        creator = db.query(User).filter(User.id == invitation.created_by).first()
        
        current_players_count = db.query(GamePlayer).filter(
            and_(
                GamePlayer.game_id == invitation.game_id,
                GamePlayer.status == GamePlayerStatus.ACCEPTED
            )
        ).count()
        
        return {
            "game_id": game.id,
            "game_name": f"Game at {game.booking.court.name if game.booking and game.booking.court else 'Unknown Court'}",
            "creator_name": creator.full_name if creator else "Unknown",
            "start_time": game.start_time,
            "end_time": game.end_time,
            "court_name": game.booking.court.name if game.booking and game.booking.court else "Unknown Court",
            "club_name": game.club.name if game.club else "Unknown Club",
            "current_players": current_players_count,
            "max_players": 4,
            "is_valid": invitation.is_valid(),
            "expires_at": invitation.expires_at
        }

# Create instance
game_invitation_crud = GameInvitationCRUD()