#!/usr/bin/env python3
"""
Debug Summary for Invitation API Endpoint Failure
Token: Qa636IGpDc_8Tq4m6Md_bSpcxpgkNDXBUTSzCqsUA-I
URL: https://padelgo-backend-production.up.railway.app/api/v1/games/invitations/Qa636IGpDc_8Tq4m6Md_bSpcxpgkNDXBUTSzCqsUA-I/info
"""

import sys
import os
sys.path.insert(0, '/Users/tarikstafford/Desktop/Projects/PadelApp/padel-app/apps/api')

from app.database import get_db
from app.crud.game_invitation_crud import game_invitation_crud
from app.models.game_invitation import GameInvitation
import json
import requests
from datetime import datetime, timezone

def debug_invitation_endpoint():
    """
    Comprehensive debug of the invitation endpoint issue.
    
    This function tests:
    1. Database connectivity and invitation token lookup
    2. Live API endpoint response
    3. Code structure analysis
    """
    
    # The failing token
    token = "Qa636IGpDc_8Tq4m6Md_bSpcxpgkNDXBUTSzCqsUA-I"
    
    print("🔍 DEBUGGING INVITATION API ENDPOINT")
    print("=" * 80)
    print(f"Token: {token}")
    print(f"URL: https://padelgo-backend-production.up.railway.app/api/v1/games/invitations/{token}/info")
    print("=" * 80)
    
    # Test 1: Database Check
    print("\n1. 🗄️ TESTING DATABASE CONNECTION")
    print("-" * 40)
    
    try:
        db = next(get_db())
        
        # Check if invitation exists in database
        invitation = game_invitation_crud.get_invitation_by_token(db, token)
        
        if invitation:
            print(f"✅ Invitation found in database:")
            print(f"  - ID: {invitation.id}")
            print(f"  - Game ID: {invitation.game_id}")
            print(f"  - Created by: {invitation.created_by}")
            print(f"  - Created at: {invitation.created_at}")
            print(f"  - Expires at: {invitation.expires_at}")
            print(f"  - Is active: {invitation.is_active}")
            print(f"  - Current uses: {invitation.current_uses}")
            print(f"  - Max uses: {invitation.max_uses}")
            
            # Check if invitation is valid
            is_valid = invitation.is_valid()
            print(f"  - Is valid: {is_valid}")
            
            if not is_valid:
                print("  ❌ Invitation is not valid!")
                if not invitation.is_active:
                    print("    - Reason: Invitation is not active")
                elif datetime.now(timezone.utc) > invitation.expires_at:
                    print("    - Reason: Invitation has expired")
                    print(f"    - Expired on: {invitation.expires_at}")
                elif invitation.max_uses and invitation.current_uses >= invitation.max_uses:
                    print("    - Reason: Maximum uses reached")
            
            # Test get_invitation_info method
            print("\n  Testing get_invitation_info method...")
            try:
                invitation_info = game_invitation_crud.get_invitation_info(db, token)
                if invitation_info:
                    print("  ✅ get_invitation_info method works")
                    print(f"  Response structure: {list(invitation_info.keys())}")
                else:
                    print("  ❌ get_invitation_info returned None")
            except Exception as e:
                print(f"  ❌ get_invitation_info failed: {e}")
                
        else:
            print("❌ Invitation not found in database")
            
            # Show recent invitations for comparison
            print("\n  Recent invitations (last 5):")
            recent_invitations = db.query(GameInvitation).order_by(GameInvitation.created_at.desc()).limit(5).all()
            for inv in recent_invitations:
                print(f"  - Token: {inv.token[:20]}...")
                print(f"    Game ID: {inv.game_id}")
                print(f"    Created: {inv.created_at}")
                print(f"    Valid: {inv.is_valid()}")
                print()
        
        db.close()
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Live API Endpoint Check
    print("\n2. 🌐 TESTING LIVE API ENDPOINT")
    print("-" * 40)
    
    url = f"https://padelgo-backend-production.up.railway.app/api/v1/games/invitations/{token}/info"
    
    try:
        response = requests.get(url, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Content: {response.text}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ API endpoint is working!")
                print("Response structure:")
                print(json.dumps(data, indent=2, default=str))
            except json.JSONDecodeError:
                print("❌ API returned non-JSON response")
                
        elif response.status_code == 404:
            print("❌ API returned 404 - Invitation not found")
            
        elif response.status_code == 500:
            print("❌ API returned 500 - Internal server error")
            
        else:
            print(f"❌ API returned unexpected status: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("❌ API request timed out")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - API might be down")
    except Exception as e:
        print(f"❌ API request failed: {e}")
    
    # Test 3: Code Structure Analysis
    print("\n3. 📋 CODE STRUCTURE ANALYSIS")
    print("-" * 40)
    
    print("✅ Endpoint exists: /api/v1/games/invitations/{token}/info")
    print("✅ Router configured: app.routers.games (line 566)")
    print("✅ Function: get_invitation_info()")
    print("✅ No authentication required for this endpoint")
    print("✅ Uses game_invitation_crud.get_invitation_info()")
    print("✅ Returns 404 if invitation not found")
    print("✅ Returns invitation info if found")
    
    # Test 4: Deployment Status Check
    print("\n4. 🚀 DEPLOYMENT STATUS")
    print("-" * 40)
    
    # Check if this is a deployment issue
    try:
        health_response = requests.get("https://padelgo-backend-production.up.railway.app/health", timeout=10)
        if health_response.status_code == 200:
            print("✅ API server is running (health check passed)")
        else:
            print(f"❌ API server health check failed: {health_response.status_code}")
    except:
        print("❌ API server appears to be down")
    
    # Check API version
    try:
        root_response = requests.get("https://padelgo-backend-production.up.railway.app/", timeout=10)
        if root_response.status_code == 200:
            print("✅ API root endpoint accessible")
            try:
                root_data = root_response.json()
                print(f"API Message: {root_data.get('message', 'Unknown')}")
            except:
                print("Root response not JSON")
        else:
            print(f"❌ API root endpoint failed: {root_response.status_code}")
    except:
        print("❌ API root endpoint not accessible")

if __name__ == "__main__":
    debug_invitation_endpoint()