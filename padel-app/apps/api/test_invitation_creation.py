#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models.game_invitation import GameInvitation
from app.models.game import Game
from app.models.user import User
from app.crud.game_invitation_crud import game_invitation_crud
from datetime import datetime, timezone
import json

def test_invitation_creation():
    """Test creating and retrieving an invitation to verify the process"""
    db = next(get_db())
    try:
        print("TESTING INVITATION CREATION PROCESS")
        print("=" * 60)
        
        # First, check if we have any games available
        games = db.query(Game).limit(5).all()
        if not games:
            print("❌ No games found in database!")
            return
        
        print(f"✅ Found {len(games)} games in database")
        
        # Check if we have any users
        users = db.query(User).limit(5).all()
        if not users:
            print("❌ No users found in database!")
            return
        
        print(f"✅ Found {len(users)} users in database")
        
        # Use the first game and user for testing
        test_game = games[0]
        test_user = users[0]
        
        print(f"\nTesting with:")
        print(f"  - Game ID: {test_game.id}")
        print(f"  - User ID: {test_user.id} ({test_user.email})")
        
        # Create a test invitation
        print("\n" + "=" * 60)
        print("CREATING TEST INVITATION")
        print("=" * 60)
        
        invitation = game_invitation_crud.create_invitation(
            db=db,
            game_id=test_game.id,
            created_by=test_user.id,
            expires_in_hours=24,
            max_uses=None
        )
        
        print(f"✅ Created invitation:")
        print(f"  - ID: {invitation.id}")
        print(f"  - Token: {invitation.token}")
        print(f"  - Game ID: {invitation.game_id}")
        print(f"  - Created by: {invitation.created_by}")
        print(f"  - Expires at: {invitation.expires_at}")
        print(f"  - Is active: {invitation.is_active}")
        print(f"  - Is valid: {invitation.is_valid()}")
        
        # Test retrieving the invitation
        print("\n" + "=" * 60)
        print("TESTING INVITATION RETRIEVAL")
        print("=" * 60)
        
        # Test get_invitation_by_token
        retrieved_invitation = game_invitation_crud.get_invitation_by_token(db, invitation.token)
        if retrieved_invitation:
            print(f"✅ Retrieved invitation by token:")
            print(f"  - ID: {retrieved_invitation.id}")
            print(f"  - Token matches: {retrieved_invitation.token == invitation.token}")
        else:
            print("❌ Failed to retrieve invitation by token!")
        
        # Test get_invitation_info
        print("\n" + "=" * 60)
        print("TESTING INVITATION INFO")
        print("=" * 60)
        
        invitation_info = game_invitation_crud.get_invitation_info(db, invitation.token)
        if invitation_info:
            print("✅ Retrieved invitation info successfully!")
            print("Structure returned:")
            print(json.dumps(invitation_info, indent=2, default=str))
        else:
            print("❌ Failed to retrieve invitation info!")
        
        # Check the problematic token
        print("\n" + "=" * 60)
        print("CHECKING PROBLEMATIC TOKEN")
        print("=" * 60)
        
        problematic_token = "r1D6pEsTGh4xmouDDzKfFBhLbw4cNfAflVf8caD7Ovg"
        problematic_invitation = game_invitation_crud.get_invitation_by_token(db, problematic_token)
        
        if problematic_invitation:
            print(f"✅ Found problematic token in database:")
            print(f"  - ID: {problematic_invitation.id}")
            print(f"  - Game ID: {problematic_invitation.game_id}")
            print(f"  - Created by: {problematic_invitation.created_by}")
            print(f"  - Expires at: {problematic_invitation.expires_at}")
            print(f"  - Is active: {problematic_invitation.is_active}")
            print(f"  - Is valid: {problematic_invitation.is_valid()}")
            
            # Check if it's expired
            if problematic_invitation.expires_at < datetime.now(timezone.utc):
                print("❌ Token is EXPIRED!")
                time_diff = datetime.now(timezone.utc) - problematic_invitation.expires_at
                print(f"  - Expired {time_diff} ago")
        else:
            print("❌ Problematic token NOT found in database!")
            
        # Show recent invitations
        print("\n" + "=" * 60)
        print("RECENT INVITATIONS")
        print("=" * 60)
        
        recent_invitations = db.query(GameInvitation).order_by(GameInvitation.created_at.desc()).limit(5).all()
        
        if recent_invitations:
            for i, inv in enumerate(recent_invitations, 1):
                status = "VALID" if inv.is_valid() else "INVALID"
                print(f"{i}. {inv.token[:15]}... - {status}")
                print(f"   Created: {inv.created_at}")
                print(f"   Expires: {inv.expires_at}")
                print(f"   Game ID: {inv.game_id}")
                print()
        else:
            print("No recent invitations found!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == '__main__':
    test_invitation_creation()