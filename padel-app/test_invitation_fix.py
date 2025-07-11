#!/usr/bin/env python3
"""
Test script to verify the invitation endpoint fix
"""
import sys
import os
import requests
import json
from typing import Dict, Any

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'apps/api'))

# Configuration
BASE_URL = "http://localhost:8000"  # Adjust if your API runs on a different port
API_BASE = f"{BASE_URL}/api/v1"

def test_invitation_endpoint(token: str) -> Dict[str, Any]:
    """Test the invitation info endpoint"""
    try:
        url = f"{API_BASE}/games/invitations/{token}/info"
        print(f"Testing URL: {url}")
        
        response = requests.get(url, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS: Invitation info retrieved")
            print(f"Game ID: {data.get('game', {}).get('id', 'Unknown')}")
            print(f"Is Valid: {data.get('is_valid', 'Unknown')}")
            print(f"Is Expired: {data.get('is_expired', 'Unknown')}")
            print(f"Can Join: {data.get('can_join', 'Unknown')}")
            return {"success": True, "data": data}
        elif response.status_code == 404:
            print("❌ ERROR: 404 - Invitation not found")
            try:
                error_data = response.json()
                print(f"Error detail: {error_data.get('detail', 'No detail provided')}")
            except:
                print(f"Raw response: {response.text}")
            return {"success": False, "error": "404 Not Found"}
        else:
            print(f"❌ ERROR: {response.status_code}")
            print(f"Response: {response.text}")
            return {"success": False, "error": f"HTTP {response.status_code}"}
            
    except requests.exceptions.RequestException as e:
        print(f"❌ REQUEST ERROR: {e}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        return {"success": False, "error": str(e)}

def test_database_direct():
    """Test the database directly to check for common issues"""
    try:
        # This would require setting up the database connection
        # For now, we'll just provide guidance
        print("\n🔍 DATABASE DEBUGGING STEPS:")
        print("1. Check if invitation tokens exist in game_invitations table")
        print("2. Verify that games have valid booking_id references")
        print("3. Check that bookings have valid court_id references")
        print("4. Verify that courts have valid club_id references")
        print("\nSQL queries to run:")
        print("SELECT * FROM game_invitations WHERE token = 'YOUR_TOKEN';")
        print("SELECT g.*, b.id as booking_exists FROM games g LEFT JOIN bookings b ON g.booking_id = b.id;")
        print("SELECT b.*, c.id as court_exists FROM bookings b LEFT JOIN courts c ON b.court_id = c.id;")
        print("SELECT c.*, cl.id as club_exists FROM courts c LEFT JOIN clubs cl ON c.club_id = cl.id;")
        
    except Exception as e:
        print(f"Database check error: {e}")

def main():
    print("🔧 INVITATION ENDPOINT FIX TESTER")
    print("=" * 50)
    
    # Test with a sample token (you'll need to provide a real one)
    test_token = input("Enter invitation token to test (or press Enter to skip): ").strip()
    
    if test_token:
        print(f"\nTesting with token: {test_token}")
        result = test_invitation_endpoint(test_token)
        
        if result["success"]:
            print("\n✅ The fix appears to be working!")
        else:
            print(f"\n❌ Issue still exists: {result['error']}")
            print("\nNext steps:")
            print("1. Check the server logs for detailed error messages")
            print("2. Verify the database contains the expected data")
            print("3. Ensure the API server is running")
    else:
        print("\nNo token provided. Here's how to test:")
        print("1. Create a game invitation through your app")
        print("2. Copy the invitation token from the URL")
        print("3. Run this script again with the token")
    
    test_database_direct()
    
    print("\n📝 WHAT THE FIX DOES:")
    print("- Adds detailed logging to track where errors occur")
    print("- Provides fallback data when database relationships fail")
    print("- Returns partial data instead of failing completely")
    print("- Logs specific error messages for debugging")

if __name__ == "__main__":
    main()