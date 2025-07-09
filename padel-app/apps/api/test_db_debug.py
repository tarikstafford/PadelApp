#!/usr/bin/env python3

import os
import sys
import requests
import json
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, '/Users/tarikstafford/Desktop/Projects/PadelApp/padel-app/apps/api')

def test_api_endpoint():
    """Test the API endpoint directly"""
    
    # The failing token
    token = "Qa636IGpDc_8Tq4m6Md_bSpcxpgkNDXBUTSzCqsUA-I"
    
    # Test URL
    url = f"https://padelgo-backend-production.up.railway.app/api/v1/games/invitations/{token}/info"
    
    print(f"Testing URL: {url}")
    print("=" * 80)
    
    try:
        # Make the request with detailed error handling
        response = requests.get(url, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
        print("=" * 80)
        
        # Print raw response content
        print("Raw Response Content:")
        print(response.text)
        print("=" * 80)
        
        # Try to parse response as JSON
        try:
            response_data = response.json()
            print("Parsed JSON Response:")
            print(json.dumps(response_data, indent=2, default=str))
        except json.JSONDecodeError:
            print("Response is not valid JSON")
            
    except requests.exceptions.Timeout:
        print("Request timed out")
    except requests.exceptions.ConnectionError:
        print("Connection error")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        
    print("=" * 80)

def test_database_connection():
    """Test if we can connect to the database"""
    try:
        from app.database import get_db
        from app.models.game_invitation import GameInvitation
        
        print("Testing database connection...")
        db = next(get_db())
        
        # Count total invitations
        total_invitations = db.query(GameInvitation).count()
        print(f"Total invitations in database: {total_invitations}")
        
        # Check for specific token
        token = "Qa636IGpDc_8Tq4m6Md_bSpcxpgkNDXBUTSzCqsUA-I"
        invitation = db.query(GameInvitation).filter(GameInvitation.token == token).first()
        
        if invitation:
            print(f"✅ Found invitation with token: {token}")
            print(f"  - ID: {invitation.id}")
            print(f"  - Game ID: {invitation.game_id}")
            print(f"  - Created by: {invitation.created_by}")
            print(f"  - Is active: {invitation.is_active}")
            print(f"  - Expires at: {invitation.expires_at}")
            print(f"  - Is valid: {invitation.is_valid()}")
        else:
            print(f"❌ No invitation found with token: {token}")
            
            # Show recent invitations
            recent_invitations = db.query(GameInvitation).order_by(GameInvitation.created_at.desc()).limit(5).all()
            print(f"\nRecent invitations (last 5):")
            for inv in recent_invitations:
                print(f"  - Token: {inv.token[:20]}...")
                print(f"    Game ID: {inv.game_id}")
                print(f"    Created: {inv.created_at}")
                print(f"    Valid: {inv.is_valid()}")
                print()
        
        db.close()
        
    except Exception as e:
        print(f"Database connection failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔍 DEBUGGING INVITATION API ENDPOINT")
    print("=" * 80)
    
    print("1. Testing API endpoint...")
    test_api_endpoint()
    
    print("\n2. Testing database connection...")
    test_database_connection()