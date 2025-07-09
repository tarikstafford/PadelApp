#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, '/Users/tarikstafford/Desktop/Projects/PadelApp/padel-app/apps/api')

from app.database import get_db
from app.crud.game_invitation_crud import game_invitation_crud
from app.models.game_invitation import GameInvitation
import json
import requests

def test_api_endpoint(token):
    """Test the API endpoint directly"""
    url = f"https://padelgo-backend-production.up.railway.app/api/v1/games/invitations/{token}/info"
    
    try:
        response = requests.get(url, timeout=30)
        print(f"API Response Status: {response.status_code}")
        print(f"API Response: {response.text}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ API endpoint working!")
                print(f"Response data: {json.dumps(data, indent=2, default=str)}")
            except:
                print("❌ API returned non-JSON response")
        else:
            print(f"❌ API returned error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ API request failed: {e}")
    
    print("=" * 50)

def debug_specific_token():
    """Debug the specific token that's failing"""
    db = next(get_db())
    try:
        # The actual token from the failing request
        token = "Qa636IGpDc_8Tq4m6Md_bSpcxpgkNDXBUTSzCqsUA-I"
        
        # Also test the API endpoint directly
        print("Testing API endpoint directly...")
        test_api_endpoint(token)
        
        print(f"Debugging token: {token}")
        print("=" * 50)
        
        # Check if invitation exists
        invitation = game_invitation_crud.get_invitation_by_token(db, token)
        if invitation:
            print(f"✅ Invitation found:")
            print(f"  - ID: {invitation.id}")
            print(f"  - Game ID: {invitation.game_id}")
            print(f"  - Created by: {invitation.created_by}")
            print(f"  - Expires at: {invitation.expires_at}")
            print(f"  - Is active: {invitation.is_active}")
            print(f"  - Is valid: {invitation.is_valid()}")
            print(f"  - Current uses: {invitation.current_uses}")
            print(f"  - Max uses: {invitation.max_uses}")
            
            # Try to get invitation info
            print("\n" + "=" * 50)
            print("Testing get_invitation_info...")
            
            try:
                invitation_info = game_invitation_crud.get_invitation_info(db, token)
                if invitation_info:
                    print("✅ get_invitation_info succeeded!")
                    print("Response structure:")
                    print(json.dumps(invitation_info, indent=2, default=str))
                else:
                    print("❌ get_invitation_info returned None")
            except Exception as e:
                print(f"❌ get_invitation_info failed: {e}")
                import traceback
                traceback.print_exc()
                
        else:
            print(f"❌ No invitation found for token: {token}")
            
            # Check if there are any invitations in the database
            print("\nChecking for any invitations in database...")
            all_invitations = db.query(GameInvitation).all()
            print(f"Total invitations in database: {len(all_invitations)}")
            
            if all_invitations:
                print("Recent invitations:")
                for inv in all_invitations[-5:]:  # Show last 5
                    print(f"  - Token: {inv.token[:20]}...")
                    print(f"    Game ID: {inv.game_id}")
                    print(f"    Valid: {inv.is_valid()}")
                    print(f"    Active: {inv.is_active}")
                    print()
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == '__main__':
    debug_specific_token()