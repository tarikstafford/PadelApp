#!/usr/bin/env python3
"""
Test script to verify tournament expiration functionality
"""
import sys
import os
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"  # Adjust if your API runs on a different port
API_BASE = f"{BASE_URL}/api/v1"

def test_tournament_expiration_status(auth_token: str = None) -> Dict[str, Any]:
    """Test the tournament expiration status endpoint"""
    try:
        url = f"{API_BASE}/tournaments/expiration-status"
        headers = {}
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
        print(f"Testing URL: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS: Retrieved tournament expiration status")
            print(f"Tournaments needing action: {data.get('total_needing_action', 0)}")
            
            registration_to_close = data.get('registration_to_close', [])
            tournaments_to_complete = data.get('tournaments_to_complete', [])
            
            print(f"\n📝 REGISTRATION TO CLOSE ({len(registration_to_close)}):")
            for tournament in registration_to_close:
                print(f"  - ID: {tournament.get('id')}, Name: {tournament.get('name')}")
                print(f"    Status: {tournament.get('status')}")
                print(f"    Deadline: {tournament.get('registration_deadline')}")
            
            print(f"\n🏁 TOURNAMENTS TO COMPLETE ({len(tournaments_to_complete)}):")
            for tournament in tournaments_to_complete:
                print(f"  - ID: {tournament.get('id')}, Name: {tournament.get('name')}")
                print(f"    Status: {tournament.get('status')}")
                print(f"    End Date: {tournament.get('end_date')}")
                print(f"    Has Unfinished Matches: {tournament.get('has_unfinished_matches')}")
            
            return {"success": True, "data": data}
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

def test_expire_past_tournaments(auth_token: str = None) -> Dict[str, Any]:
    """Test the expire past tournaments endpoint"""
    try:
        url = f"{API_BASE}/tournaments/expire-past-tournaments"
        headers = {}
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
        print(f"Testing URL: {url}")
        response = requests.post(url, headers=headers, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS: Tournament expiration completed")
            print(f"Message: {data.get('message')}")
            print(f"Registration closed: {data.get('registration_closed')}")
            print(f"Completed: {data.get('completed')}")
            print(f"Registration closed IDs: {data.get('registration_closed_ids')}")
            print(f"Completed IDs: {data.get('completed_ids')}")
            return {"success": True, "data": data}
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

def test_single_tournament_expiration(tournament_id: int, auth_token: str = None) -> Dict[str, Any]:
    """Test expiring a single tournament"""
    try:
        url = f"{API_BASE}/tournaments/{tournament_id}/expire"
        headers = {}
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
        print(f"Testing URL: {url}")
        response = requests.post(url, headers=headers, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS: Single tournament expiration completed")
            print(f"Message: {data.get('message')}")
            print(f"Tournament ID: {data.get('tournament_id')}")
            print(f"Original Status: {data.get('original_status')}")
            print(f"New Status: {data.get('new_status')}")
            print(f"Action Taken: {data.get('action_taken')}")
            return {"success": True, "data": data}
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

def simulate_database_query():
    """Simulate checking database for expired tournaments"""
    print("\n🔍 DATABASE DEBUGGING QUERIES:")
    print("Run these SQL queries to check tournament status:")
    
    current_time = datetime.now().isoformat()
    
    print(f"\n1. Find tournaments with expired registration (current time: {current_time}):")
    print("""
SELECT id, name, status, registration_deadline, club_id 
FROM tournaments 
WHERE status = 'REGISTRATION_OPEN' 
AND registration_deadline < NOW();
""")
    
    print("\n2. Find tournaments that should be completed:")
    print("""
SELECT id, name, status, end_date, club_id 
FROM tournaments 
WHERE status IN ('REGISTRATION_CLOSED', 'IN_PROGRESS') 
AND end_date < NOW();
""")
    
    print("\n3. Check all tournament statuses:")
    print("""
SELECT id, name, status, registration_deadline, start_date, end_date, club_id 
FROM tournaments 
ORDER BY registration_deadline DESC;
""")

def main():
    print("🏆 TOURNAMENT EXPIRATION SYSTEM TESTER")
    print("=" * 60)
    
    auth_token = input("Enter your authentication token (or press Enter to skip): ").strip()
    
    if not auth_token:
        print("\n⚠️  No authentication token provided.")
        print("You'll need to authenticate to test the endpoints.")
        print("Get your token from the login response or browser developer tools.")
        
        simulate_database_query()
        return
    
    print("\n1. Testing tournament expiration status endpoint...")
    status_result = test_tournament_expiration_status(auth_token)
    
    if status_result["success"]:
        data = status_result["data"]
        needing_action = data.get("total_needing_action", 0)
        
        if needing_action > 0:
            print(f"\n2. Found {needing_action} tournaments needing action. Testing expiration...")
            expire_result = test_expire_past_tournaments(auth_token)
            
            if expire_result["success"]:
                print("\n✅ Tournament expiration system is working correctly!")
            else:
                print(f"\n❌ Tournament expiration failed: {expire_result['error']}")
        else:
            print("\n✅ No tournaments need expiration at this time.")
    else:
        print(f"\n❌ Failed to check expiration status: {status_result['error']}")
    
    # Test single tournament expiration
    tournament_id = input("\nEnter a tournament ID to test single expiration (or press Enter to skip): ").strip()
    if tournament_id and tournament_id.isdigit():
        print(f"\n3. Testing single tournament expiration for ID {tournament_id}...")
        single_result = test_single_tournament_expiration(int(tournament_id), auth_token)
        
        if single_result["success"]:
            print("\n✅ Single tournament expiration test completed!")
        else:
            print(f"\n❌ Single tournament expiration failed: {single_result['error']}")
    
    simulate_database_query()
    
    print("\n📋 NEXT STEPS:")
    print("1. Set up a scheduled job to call /tournaments/expire-past-tournaments")
    print("2. Consider using cron job, APScheduler, or Celery for automation")
    print("3. Monitor the expiration status endpoint for tournaments needing action")
    print("4. Update tournament display logic to filter out expired tournaments")

if __name__ == "__main__":
    main()