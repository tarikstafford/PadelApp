#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, '/Users/tarikstafford/Desktop/Projects/PadelApp/padel-app/apps/api')

from app.database import get_db
from app.crud.game_invitation_crud import game_invitation_crud
import json

def test_invitation_info():
    db = next(get_db())
    try:
        # Test with a sample token (replace with actual token)
        test_token = "sample_token"  # Replace with a real token for testing
        
        print(f"Testing invitation info for token: {test_token}")
        
        invitation_info = game_invitation_crud.get_invitation_info(db, test_token)
        
        if invitation_info:
            print("Success! Invitation info retrieved:")
            print(json.dumps(invitation_info, indent=2, default=str))
        else:
            print("No invitation found for this token")
            
        # Also test getting invitation by token directly
        invitation = game_invitation_crud.get_invitation_by_token(db, test_token)
        if invitation:
            print(f"\nInvitation found: ID={invitation.id}, Game ID={invitation.game_id}")
            print(f"Valid: {invitation.is_valid()}")
        else:
            print("No invitation object found")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == '__main__':
    test_invitation_info()