#!/usr/bin/env python3
"""
Minimal script to test token lookup in database
"""
import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from app.database import get_db
    from app.models.game_invitation import GameInvitation
    from app.crud.game_invitation_crud import game_invitation_crud
    
    def test_token_lookup():
        """Test if the specific token exists in the database"""
        token = "Qa636IGpDc_8Tq4m6Md_bSpcxpgkNDXBUTSzCqsUA-I"
        
        print(f"Testing token: {token}")
        print("=" * 50)
        
        try:
            db = next(get_db())
            
            # First, check if we can connect to the database
            print("Database connection: OK")
            
            # Check total number of invitations
            total_invitations = db.query(GameInvitation).count()
            print(f"Total invitations in database: {total_invitations}")
            
            # Try to find the specific token
            invitation = game_invitation_crud.get_invitation_by_token(db, token)
            
            if invitation:
                print("✅ Token found in database!")
                print(f"  - ID: {invitation.id}")
                print(f"  - Game ID: {invitation.game_id}")
                print(f"  - Created by: {invitation.created_by}")
                print(f"  - Expires at: {invitation.expires_at}")
                print(f"  - Is active: {invitation.is_active}")
                print(f"  - Is valid: {invitation.is_valid()}")
                print(f"  - Current uses: {invitation.current_uses}")
                print(f"  - Max uses: {invitation.max_uses}")
                
                # Try to get full invitation info
                print("\nTesting get_invitation_info...")
                invitation_info = game_invitation_crud.get_invitation_info(db, token)
                if invitation_info:
                    print("✅ get_invitation_info succeeded!")
                    print(f"  - Game ID: {invitation_info['game']['id']}")
                    print(f"  - Can join: {invitation_info['can_join']}")
                    print(f"  - Is valid: {invitation_info['is_valid']}")
                    print(f"  - Is expired: {invitation_info['is_expired']}")
                    print(f"  - Is full: {invitation_info['is_full']}")
                else:
                    print("❌ get_invitation_info returned None")
                    
            else:
                print("❌ Token not found in database")
                
                # Show some recent invitations for debugging
                print("\nRecent invitations in database:")
                recent_invitations = db.query(GameInvitation).order_by(GameInvitation.created_at.desc()).limit(5).all()
                for inv in recent_invitations:
                    print(f"  - Token: {inv.token[:20]}...")
                    print(f"    Game ID: {inv.game_id}")
                    print(f"    Created: {inv.created_at}")
                    print(f"    Valid: {inv.is_valid()}")
                    print(f"    Active: {inv.is_active}")
                    print()
                    
        except Exception as e:
            print(f"❌ Database error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            db.close()
            
    if __name__ == "__main__":
        test_token_lookup()
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("This suggests either:")
    print("1. Database connection issues")
    print("2. Missing environment variables")
    print("3. Dependencies not installed")
    print("4. Python path issues")