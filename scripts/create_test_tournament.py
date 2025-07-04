#!/usr/bin/env python3
"""
Create a test tournament with proper categories to test the full flow
"""

import requests
import json
from datetime import datetime, timedelta

API_BASE_URL = "https://padelgo-backend-production.up.railway.app/api/v1"

def create_admin_user():
    """Create and login as admin"""
    admin_data = {
        "full_name": "Test Admin",
        "email": "testadmin@example.com",
        "password": "admin123"
    }
    
    # Try to login first
    try:
        response = requests.post(f"{API_BASE_URL}/auth/login", json={
            "email": admin_data["email"],
            "password": admin_data["password"]
        })
        
        if response.status_code == 200:
            data = response.json()
            print("✓ Admin logged in successfully")
            return data.get("access_token")
    except:
        pass
    
    # Register if login failed
    try:
        response = requests.post(f"{API_BASE_URL}/auth/register", json=admin_data)
        if response.status_code == 201:
            data = response.json()
            print("✓ Admin user created and logged in")
            return data.get("access_token")
        else:
            print(f"✗ Failed to create admin: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ Error creating admin: {str(e)}")
    
    return None

def create_tournament_with_categories(admin_token):
    """Create a tournament with proper categories"""
    
    # Get current time + 1 week for tournament dates
    now = datetime.now()
    start_date = now + timedelta(days=7)
    end_date = start_date + timedelta(days=2)
    registration_deadline = now + timedelta(days=5)
    
    tournament_data = {
        "name": "Test Tournament with Categories",
        "description": "A test tournament to verify category functionality",
        "tournament_type": "DOUBLE_ELIMINATION",
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(), 
        "registration_deadline": registration_deadline.isoformat(),
        "max_participants": 32,
        "entry_fee": 0.0,
        "categories": [
            {
                "category": "BRONZE",
                "max_participants": 16
            },
            {
                "category": "SILVER", 
                "max_participants": 16
            }
        ],
        "court_ids": [1]  # Assuming court ID 1 exists
    }
    
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/tournaments", json=tournament_data, headers=headers)
        
        if response.status_code == 201:
            tournament = response.json()
            print(f"✓ Tournament created successfully!")
            print(f"  ID: {tournament.get('id')}")
            print(f"  Name: {tournament.get('name')}")
            print(f"  Categories: {len(tournament.get('categories', []))} categories")
            return tournament.get('id')
        else:
            print(f"✗ Failed to create tournament: {response.status_code}")
            print(f"  Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"✗ Error creating tournament: {str(e)}")
        return None

def test_tournament_with_categories(tournament_id, admin_token):
    """Test the created tournament"""
    
    # Get tournament details
    try:
        response = requests.get(f"{API_BASE_URL}/tournaments/{tournament_id}")
        if response.status_code == 200:
            tournament = response.json()
            print(f"\\n✓ Tournament details retrieved:")
            print(f"  ID: {tournament.get('id')}")
            print(f"  Name: {tournament.get('name')}")
            print(f"  Categories: {tournament.get('categories')}")
            print(f"  Total registered teams: {tournament.get('total_registered_teams')}")
            
            # Now test team eligibility against this tournament
            print(f"\\nTesting team eligibility against tournament {tournament_id}...")
            
            # Use existing test team (should exist from previous tests)
            test_team_eligibility(tournament_id)
            
        else:
            print(f"✗ Failed to get tournament details: {response.status_code}")
    except Exception as e:
        print(f"✗ Error getting tournament: {str(e)}")

def test_team_eligibility(tournament_id):
    """Test team eligibility with existing teams"""
    
    # Try to find existing teams by creating a test user and checking their teams
    test_user_data = {
        "full_name": "Eligibility Test User",
        "email": "eligibilitytest@example.com", 
        "password": "test123"
    }
    
    try:
        # Login existing user
        response = requests.post(f"{API_BASE_URL}/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        
        if response.status_code == 200:
            auth_data = response.json()
            token = auth_data.get("access_token")
            
            # Get user teams
            headers = {"Authorization": f"Bearer {token}"}
            teams_response = requests.get(f"{API_BASE_URL}/users/me/teams", headers=headers)
            
            if teams_response.status_code == 200:
                teams = teams_response.json()
                print(f"  Found {len(teams)} teams for user")
                
                for team in teams:
                    team_id = team.get('id')
                    team_name = team.get('name', 'Unknown')
                    
                    # Check eligibility
                    eligibility_response = requests.get(
                        f"{API_BASE_URL}/tournaments/{tournament_id}/eligibility/{team_id}", 
                        headers=headers
                    )
                    
                    if eligibility_response.status_code == 200:
                        eligibility = eligibility_response.json()
                        eligible = eligibility.get('eligible', False)
                        categories = eligibility.get('eligible_categories', [])
                        
                        print(f"  Team '{team_name}': {'Eligible' if eligible else 'Not eligible'}")
                        if eligible:
                            print(f"    Eligible categories: {categories}")
                        else:
                            print(f"    Reason: {eligibility.get('reason', 'Unknown')}")
                    else:
                        print(f"  Team '{team_name}': Could not check eligibility")
            else:
                print("  No teams found for user")
        else:
            print("  Could not login test user")
            
    except Exception as e:
        print(f"  Error testing eligibility: {str(e)}")

def main():
    print("Creating test tournament with categories...")
    print("=" * 50)
    
    # Step 1: Get admin token
    admin_token = create_admin_user()
    if not admin_token:
        print("✗ Failed to get admin token")
        return
    
    # Step 2: Create tournament with categories
    tournament_id = create_tournament_with_categories(admin_token)
    if not tournament_id:
        print("✗ Failed to create tournament")
        return
    
    # Step 3: Test the tournament
    test_tournament_with_categories(tournament_id, admin_token)
    
    print("\\n" + "=" * 50)
    print("Test tournament creation completed!")
    print(f"Tournament ID: {tournament_id}")
    print("You can now test team registration with this tournament.")

if __name__ == "__main__":
    main()