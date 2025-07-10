from typing import Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.game import Game
from app.models.game_invitation import GameInvitation
from app.models.game_player import GamePlayer, GamePlayerStatus
from app.models.user import User


class GameInvitationCRUD:
    def create_invitation(
        self,
        db: Session,
        game_id: int,
        created_by: int,
        expires_in_hours: int = 24,
        max_uses: Optional[int] = None,
    ) -> GameInvitation:
        """Create a new game invitation"""
        invitation = GameInvitation.create_invitation(
            game_id=game_id,
            created_by=created_by,
            expires_in_hours=expires_in_hours,
            max_uses=max_uses,
        )
        db.add(invitation)
        db.commit()
        db.refresh(invitation)
        return invitation

    def get_invitation_by_token(
        self, db: Session, token: str
    ) -> Optional[GameInvitation]:
        """Get invitation by token"""
        return db.query(GameInvitation).filter(GameInvitation.token == token).first()

    def get_invitations_for_game(
        self, db: Session, game_id: int
    ) -> list[GameInvitation]:
        """Get all invitations for a specific game"""
        return db.query(GameInvitation).filter(GameInvitation.game_id == game_id).all()

    def deactivate_invitation(self, db: Session, invitation_id: int) -> bool:
        """Deactivate an invitation"""
        invitation = (
            db.query(GameInvitation).filter(GameInvitation.id == invitation_id).first()
        )
        if invitation:
            invitation.is_active = False
            db.commit()
            return True
        return False

    def check_user_onboarding_status(self, db: Session, user_id: int) -> bool:
        """Check if user has completed onboarding"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        return user.onboarding_completed

    def accept_invitation_with_onboarding_check(self, db: Session, token: str, user_id: int) -> dict:
        """Accept a game invitation with onboarding status check"""
        invitation = self.get_invitation_by_token(db, token)

        if not invitation:
            return {"success": False, "message": "Invitation not found"}

        if not invitation.is_valid():
            return {
                "success": False,
                "message": "Invitation has expired or is no longer valid",
            }

        # Check if user has completed onboarding
        if not self.check_user_onboarding_status(db, user_id):
            return {
                "success": False,
                "message": "Onboarding required before joining game",
                "requires_onboarding": True,
                "game_id": invitation.game_id,
                "invitation_token": token,
            }

        # Continue with normal invitation acceptance
        return self.accept_invitation(db, token, user_id)

    def accept_invitation(self, db: Session, token: str, user_id: int) -> dict:
        """Accept a game invitation and add user to game"""
        invitation = self.get_invitation_by_token(db, token)

        if not invitation:
            return {"success": False, "message": "Invitation not found"}

        if not invitation.is_valid():
            return {
                "success": False,
                "message": "Invitation has expired or is no longer valid",
            }

        # Check if user is already in the game
        existing_player = (
            db.query(GamePlayer)
            .filter(
                and_(
                    GamePlayer.game_id == invitation.game_id,
                    GamePlayer.user_id == user_id,
                )
            )
            .first()
        )

        if existing_player:
            return {"success": False, "message": "You are already part of this game"}

        # Check if game is full
        game = db.query(Game).filter(Game.id == invitation.game_id).first()
        if not game:
            return {"success": False, "message": "Game not found"}

        current_players_count = (
            db.query(GamePlayer)
            .filter(
                and_(
                    GamePlayer.game_id == invitation.game_id,
                    GamePlayer.status == GamePlayerStatus.ACCEPTED,
                )
            )
            .count()
        )

        if current_players_count >= 4:  # Max players per game
            return {"success": False, "message": "Game is full"}

        # Add user to game
        from app.crud.game_player_crud import game_player_crud  # noqa: PLC0415

        game_player = game_player_crud.add_player_to_game(
            db=db,
            game_id=invitation.game_id,
            user_id=user_id,
            status=GamePlayerStatus.ACCEPTED,
        )

        # Increment invitation usage
        invitation.increment_usage()
        db.commit()

        return {
            "success": True,
            "message": "Successfully joined the game!",
            "game_id": invitation.game_id,
            "game_player": game_player,
        }

    def complete_onboarding_and_join_game(self, db: Session, token: str, user_id: int) -> dict:
        """Complete user onboarding and immediately join the game"""
        # First, complete onboarding
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"success": False, "message": "User not found"}

        # Update onboarding status
        from datetime import datetime
        user.onboarding_completed = True
        user.onboarding_completed_at = datetime.utcnow()
        db.add(user)
        db.commit()

        # Now accept the invitation
        return self.accept_invitation(db, token, user_id)

    def get_invitation_info(self, db: Session, token: str) -> Optional[dict]:
        """Get public information about an invitation (for preview before auth)"""
        try:
            invitation = self.get_invitation_by_token(db, token)

            if not invitation:
                return None

            # Get the game record without complex joinedload operations
            game = db.query(Game).filter(Game.id == invitation.game_id).first()
            if not game:
                return None

            # Get creator safely
            creator = db.query(User).filter(User.id == invitation.created_by).first()

            # Count current players safely
            current_players_count = (
                db.query(GamePlayer)
                .filter(
                    and_(
                        GamePlayer.game_id == invitation.game_id,
                        GamePlayer.status == GamePlayerStatus.ACCEPTED,
                    )
                )
                .count()
            )

            # Build booking info safely
            booking_info = None
            if game.booking_id:
                try:
                    from app.models.booking import Booking
                    from app.models.court import Court
                    from app.models.club import Club

                    booking = db.query(Booking).filter(Booking.id == game.booking_id).first()
                    if booking:
                        court_info = None
                        if booking.court_id:
                            court = db.query(Court).filter(Court.id == booking.court_id).first()
                            if court:
                                club_info = None
                                if court.club_id:
                                    court_club = db.query(Club).filter(Club.id == court.club_id).first()
                                    if court_club:
                                        club_info = {
                                            "id": court_club.id,
                                            "name": court_club.name,
                                        }
                                court_info = {
                                    "id": court.id,
                                    "name": court.name,
                                    "club": club_info,
                                }

                        booking_info = {
                            "id": booking.id,
                            "start_time": booking.start_time.isoformat() if booking.start_time else None,
                            "end_time": booking.end_time.isoformat() if booking.end_time else None,
                            "court": court_info,
                        }
                except Exception:
                    # If booking relationships fail, use fallback
                    booking_info = {
                        "id": game.booking_id,
                        "start_time": game.start_time.isoformat() if game.start_time else None,
                        "end_time": game.end_time.isoformat() if game.end_time else None,
                        "court": {
                            "id": None,
                            "name": "Unknown Court",
                            "club": {"id": game.club_id, "name": "Unknown Club"},
                        },
                    }

            # Get game club info safely
            game_club_info = None
            if game.club_id:
                try:
                    from app.models.club import Club
                    game_club = db.query(Club).filter(Club.id == game.club_id).first()
                    if game_club:
                        game_club_info = {
                            "id": game_club.id,
                            "name": game_club.name,
                        }
                except Exception:
                    game_club_info = {
                        "id": game.club_id,
                        "name": "Unknown Club",
                    }

            # Get players safely
            players_info = []
            try:
                players = (
                    db.query(GamePlayer)
                    .filter(
                        and_(
                            GamePlayer.game_id == invitation.game_id,
                            GamePlayer.status == GamePlayerStatus.ACCEPTED,
                        )
                    )
                    .all()
                )

                for player in players:
                    try:
                        user = db.query(User).filter(User.id == player.user_id).first()
                        if user:
                            players_info.append({
                                "user_id": player.user_id,
                                "status": player.status.value,
                                "user": {
                                    "id": user.id,
                                    "full_name": user.full_name,
                                    "email": user.email,
                                },
                                "elo_rating": getattr(user, 'elo_rating', 1000),
                            })
                    except Exception:
                        # Skip problematic players
                        continue
            except Exception:
                # If players query fails, return empty list
                players_info = []

            # Return the complete game object structure for frontend compatibility
            return {
                "game": {
                    "id": game.id,
                    "club_id": game.club_id,
                    "booking_id": game.booking_id,
                    "game_type": game.game_type,
                    "game_status": game.game_status,
                    "skill_level": game.skill_level,
                    "start_time": game.start_time.isoformat() if game.start_time else None,
                    "end_time": game.end_time.isoformat() if game.end_time else None,
                    "booking": booking_info,
                    "club": game_club_info,
                    "players": players_info,
                },
                "creator": {
                    "id": creator.id if creator else invitation.created_by,
                    "full_name": creator.full_name if creator else "Unknown",
                    "email": creator.email if creator else "unknown@email.com",
                },
                "invitation_token": invitation.token,
                "is_valid": invitation.is_valid(),
                "is_expired": not invitation.is_valid(),
                "is_full": current_players_count >= 4,
                "can_join": invitation.is_valid() and current_players_count < 4,
                "expires_at": invitation.expires_at.isoformat() if invitation.expires_at else None,
            }

        except Exception as e:
            # Log the error but don't crash
            print(f"Error in get_invitation_info: {e}")
            return None


# Create instance
game_invitation_crud = GameInvitationCRUD()
