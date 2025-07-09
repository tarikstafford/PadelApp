#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models.game_invitation import GameInvitation
from app.models.game import Game
from app.models.user import User
from datetime import datetime, timezone
import json

def check_token_status():
    """Check the status of the failing token and recent invitations"""
    db = next(get_db())
    try:
        # The new failing token
        token = "r1D6pEsTGh4xmouDDzKfFBhLbw4cNfAflVf8caD7Ovg"
        
        print(f"Checking token: {token}")
        print("=" * 80)
        
        # Check if this specific token exists
        invitation = db.query(GameInvitation).filter(GameInvitation.token == token).first()
        
        if invitation:
            print("✅ Token found in database!")
            print(f"  - ID: {invitation.id}")
            print(f"  - Game ID: {invitation.game_id}")
            print(f"  - Created by: {invitation.created_by}")
            print(f"  - Created at: {invitation.created_at}")
            print(f"  - Expires at: {invitation.expires_at}")
            print(f"  - Is active: {invitation.is_active}")
            print(f"  - Current uses: {invitation.current_uses}")
            print(f"  - Max uses: {invitation.max_uses}")
            print(f"  - Is valid: {invitation.is_valid()}")
            
            # Check if it's expired
            if invitation.expires_at and invitation.expires_at < datetime.now(timezone.utc):
                print("❌ Token is EXPIRED!")
                time_diff = datetime.now(timezone.utc) - invitation.expires_at
                print(f"  - Expired {time_diff} ago")
            else:
                print("✅ Token is NOT expired")
                
        else:
            print("❌ Token NOT found in database!")
            
        print("\n" + "=" * 80)
        print("RECENT INVITATIONS IN DATABASE:")
        print("=" * 80)
        
        # Get recent invitations
        recent_invitations = (
            db.query(GameInvitation)
            .order_by(GameInvitation.created_at.desc())
            .limit(10)
            .all()
        )
        
        if recent_invitations:
            print(f"Found {len(recent_invitations)} recent invitations:")
            for i, inv in enumerate(recent_invitations, 1):
                status = "✅ VALID" if inv.is_valid() else "❌ INVALID"
                active = "ACTIVE" if inv.is_active else "INACTIVE"
                expired = "EXPIRED" if inv.expires_at and inv.expires_at < datetime.now(timezone.utc) else "NOT EXPIRED"
                
                print(f"\n{i}. Token: {inv.token[:20]}...{inv.token[-10:]}")
                print(f"   - Created: {inv.created_at}")
                print(f"   - Expires: {inv.expires_at}")
                print(f"   - Status: {status} | {active} | {expired}")
                print(f"   - Game ID: {inv.game_id}")
                print(f"   - Uses: {inv.current_uses}/{inv.max_uses if inv.max_uses else 'unlimited'}")
                
                # Check if game exists
                game = db.query(Game).filter(Game.id == inv.game_id).first()
                if game:
                    print(f"   - Game: {game.game_type} (Status: {game.game_status})")
                else:
                    print(f"   - Game: ❌ NOT FOUND")
                    
                # Check creator
                creator = db.query(User).filter(User.id == inv.created_by).first()
                if creator:
                    print(f"   - Creator: {creator.full_name} ({creator.email})")
                else:
                    print(f"   - Creator: ❌ NOT FOUND")
        else:
            print("No invitations found in database!")
            
        print("\n" + "=" * 80)
        print("DATABASE STATS:")
        print("=" * 80)
        
        total_invitations = db.query(GameInvitation).count()
        active_invitations = db.query(GameInvitation).filter(GameInvitation.is_active == True).count()
        valid_invitations = 0
        
        # Count valid invitations (not expired)
        all_invitations = db.query(GameInvitation).all()
        for inv in all_invitations:
            if inv.is_valid():
                valid_invitations += 1
        
        print(f"Total invitations: {total_invitations}")
        print(f"Active invitations: {active_invitations}")
        print(f"Valid (not expired) invitations: {valid_invitations}")
        
        # Check for any tokens similar to the failing one
        print("\n" + "=" * 80)
        print("CHECKING FOR SIMILAR TOKENS:")
        print("=" * 80)
        
        # Check for tokens that start with the same characters
        similar_tokens = (
            db.query(GameInvitation)
            .filter(GameInvitation.token.like(f"{token[:10]}%"))
            .all()
        )
        
        if similar_tokens:
            print(f"Found {len(similar_tokens)} tokens starting with '{token[:10]}':")
            for inv in similar_tokens:
                print(f"  - {inv.token}")
        else:
            print(f"No tokens found starting with '{token[:10]}'")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == '__main__':
    check_token_status()