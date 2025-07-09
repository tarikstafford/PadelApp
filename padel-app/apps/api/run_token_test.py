#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models.game_invitation import GameInvitation
from app.models.game import Game
from app.models.user import User
from sqlalchemy import text

def test_token_exists():
    """Simple test to check if token exists in database"""
    db = next(get_db())
    try:
        token = "Qa636IGpDc_8Tq4m6Md_bSpcxpgkNDXBUTSzCqsUA-I"
        
        print(f"Testing token: {token}")
        print("=" * 50)
        
        # Simple query to check if token exists
        invitation = db.query(GameInvitation).filter(GameInvitation.token == token).first()
        
        if invitation:
            print("✅ Token found in database!")
            print(f"  - ID: {invitation.id}")
            print(f"  - Game ID: {invitation.game_id}")
            print(f"  - Created by: {invitation.created_by}")
            print(f"  - Expires at: {invitation.expires_at}")
            print(f"  - Is active: {invitation.is_active}")
            print(f"  - Is valid: {invitation.is_valid()}")
            
            # Check if game exists
            game = db.query(Game).filter(Game.id == invitation.game_id).first()
            if game:
                print(f"✅ Associated game found (ID: {game.id})")
                print(f"  - Game type: {game.game_type}")
                print(f"  - Game status: {game.game_status}")
                print(f"  - Has booking: {game.booking_id is not None}")
                print(f"  - Has club: {game.club_id is not None}")
            else:
                print("❌ Associated game NOT found!")
                
            # Check creator
            creator = db.query(User).filter(User.id == invitation.created_by).first()
            if creator:
                print(f"✅ Creator found: {creator.full_name}")
            else:
                print("❌ Creator NOT found!")
                
        else:
            print("❌ Token NOT found in database!")
            
            # Check if there are any invitations at all
            total_invitations = db.query(GameInvitation).count()
            print(f"Total invitations in database: {total_invitations}")
            
            if total_invitations > 0:
                print("Recent invitations:")
                recent = db.query(GameInvitation).order_by(GameInvitation.id.desc()).limit(5).all()
                for inv in recent:
                    print(f"  - {inv.token[:20]}... (expires: {inv.expires_at})")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == '__main__':
    test_token_exists()