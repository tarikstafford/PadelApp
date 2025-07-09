#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from typing import Optional
from sqlalchemy import and_
from sqlalchemy.orm import Session
from app.models.game import Game
from app.models.game_invitation import GameInvitation
from app.models.game_player import GamePlayer, GamePlayerStatus
from app.models.user import User
from app.models.booking import Booking
from app.models.court import Court
from app.models.club import Club

def safer_get_invitation_info(db: Session, token: str) -> Optional[dict]:
    """
    Safer version of get_invitation_info that handles missing relationships gracefully
    """
    try:
        # First get the invitation
        invitation = db.query(GameInvitation).filter(GameInvitation.token == token).first()
        
        if not invitation:
            print(f"❌ No invitation found for token: {token}")
            return None
        
        print(f"✅ Found invitation ID: {invitation.id}")
        print(f"   - Game ID: {invitation.game_id}")
        print(f"   - Created by: {invitation.created_by}")
        print(f"   - Is valid: {invitation.is_valid()}")
        
        # Get the game record
        game = db.query(Game).filter(Game.id == invitation.game_id).first()
        if not game:
            print(f"❌ No game found for ID: {invitation.game_id}")
            return None
        
        print(f"✅ Found game: {game.id}")
        print(f"   - Game type: {game.game_type}")
        print(f"   - Game status: {game.game_status}")
        print(f"   - Booking ID: {game.booking_id}")
        print(f"   - Club ID: {game.club_id}")
        
        # Get creator (with fallback)
        creator = db.query(User).filter(User.id == invitation.created_by).first()
        creator_info = {
            "id": creator.id if creator else invitation.created_by,
            "full_name": creator.full_name if creator else "Unknown",
            "email": creator.email if creator else "unknown@email.com",
        }
        
        # Count current players (with error handling)
        try:
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
        except Exception as e:
            print(f"⚠️ Error counting players: {e}")
            current_players_count = 0
        
        # Get booking info safely
        booking_info = None
        if game.booking_id:
            try:
                booking = db.query(Booking).filter(Booking.id == game.booking_id).first()
                if booking:
                    print(f"✅ Found booking: {booking.id}")
                    
                    # Get court info safely
                    court_info = None
                    if booking.court_id:
                        try:
                            court = db.query(Court).filter(Court.id == booking.court_id).first()
                            if court:
                                print(f"✅ Found court: {court.name}")
                                
                                # Get club info safely
                                club_info = None
                                if court.club_id:
                                    try:
                                        court_club = db.query(Club).filter(Club.id == court.club_id).first()
                                        if court_club:
                                            print(f"✅ Found court club: {court_club.name}")
                                            club_info = {
                                                "id": court_club.id,
                                                "name": court_club.name,
                                            }
                                    except Exception as e:
                                        print(f"⚠️ Error getting court club: {e}")
                                
                                court_info = {
                                    "id": court.id,
                                    "name": court.name,
                                    "club": club_info,
                                }
                        except Exception as e:
                            print(f"⚠️ Error getting court: {e}")
                    
                    booking_info = {
                        "id": booking.id,
                        "start_time": booking.start_time.isoformat() if booking.start_time else None,
                        "end_time": booking.end_time.isoformat() if booking.end_time else None,
                        "court": court_info,
                    }
            except Exception as e:
                print(f"⚠️ Error getting booking: {e}")
        
        # Get game club info if no booking club
        game_club_info = None
        if game.club_id:
            try:
                game_club = db.query(Club).filter(Club.id == game.club_id).first()
                if game_club:
                    print(f"✅ Found game club: {game_club.name}")
                    game_club_info = {
                        "id": game_club.id,
                        "name": game_club.name,
                    }
            except Exception as e:
                print(f"⚠️ Error getting game club: {e}")
        
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
                except Exception as e:
                    print(f"⚠️ Error getting player {player.user_id}: {e}")
        except Exception as e:
            print(f"⚠️ Error getting players: {e}")
        
        # Build response with safe fallbacks
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
            "creator": creator_info,
            "invitation_token": invitation.token,
            "is_valid": invitation.is_valid(),
            "is_expired": not invitation.is_valid(),
            "is_full": current_players_count >= 4,
            "can_join": invitation.is_valid() and current_players_count < 4,
            "expires_at": invitation.expires_at.isoformat() if invitation.expires_at else None,
        }
        
    except Exception as e:
        print(f"❌ Error in safer_get_invitation_info: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_safer_method():
    """Test the safer method with the problematic token"""
    from app.database import get_db
    
    db = next(get_db())
    try:
        token = "Qa636IGpDc_8Tq4m6Md_bSpcxpgkNDXBUTSzCqsUA-I"
        print(f"Testing safer method with token: {token}")
        print("=" * 60)
        
        result = safer_get_invitation_info(db, token)
        
        if result:
            print("✅ Safer method succeeded!")
            print("Response structure:")
            import json
            print(json.dumps(result, indent=2, default=str))
        else:
            print("❌ Safer method returned None")
            
    except Exception as e:
        print(f"❌ Error in test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == '__main__':
    test_safer_method()