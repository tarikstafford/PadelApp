#!/usr/bin/env python3
"""
Quick check of tournament categories
"""

import requests
import json

API_BASE_URL = "https://padelgo-backend-production.up.railway.app/api/v1"

def check_tournament_categories():
    """Check tournament categories"""
    
    print("Checking Tournament 1 categories...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/tournaments/1")
        if response.status_code == 200:
            tournament = response.json()
            print(f"✓ Tournament: {tournament.get('name')}")
            print(f"  Status: {tournament.get('status')}")
            print(f"  Categories in API response: {len(tournament.get('categories', []))}")
            
            if tournament.get('categories'):
                for cat in tournament['categories']:
                    print(f"    - {cat}")
            else:
                print("    (No categories in API response)")
                
            print(f"  Total registered teams: {tournament.get('total_registered_teams', 0)}")
            return tournament
        else:
            print(f"✗ Failed to get tournament: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"✗ Error: {str(e)}")
    
    return None

def check_all_tournaments():
    """Check all tournaments"""
    
    print("\nChecking all tournaments...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/tournaments/")
        if response.status_code == 200:
            tournaments = response.json()
            print(f"✓ Found {len(tournaments)} tournaments:")
            
            for tournament in tournaments:
                print(f"  Tournament {tournament.get('id')}: {tournament.get('name')}")
                print(f"    Status: {tournament.get('status')}")
                print(f"    Teams: {tournament.get('total_registered_teams', 0)}")
        else:
            print(f"✗ Failed to get tournaments: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {str(e)}")

def test_team_eligibility_quick():
    """Quick test of team eligibility"""
    
    print("\nTesting team eligibility...")
    
    # Try to login a test user
    test_user = {
        "email": "player01@populate.example",
        "password": "player123"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/auth/login", json=test_user)
        if response.status_code == 200:
            auth_data = response.json()
            token = auth_data.get("access_token")
            
            # Get user details
            headers = {"Authorization": f"Bearer {token}"}
            me_response = requests.get(f"{API_BASE_URL}/users/me", headers=headers)
            
            if me_response.status_code == 200:
                user = me_response.json()
                print(f"✓ Logged in as: {user.get('full_name')}")
                
                # Get teams
                teams_response = requests.get(f"{API_BASE_URL}/users/me/teams", headers=headers)
                
                if teams_response.status_code == 200:
                    teams = teams_response.json()
                    print(f"  Found {len(teams)} teams")
                    
                    if teams:
                        team = teams[0]
                        team_id = team.get('id')
                        print(f"  Testing team: {team.get('name')} (ID: {team_id})")
                        
                        # Check eligibility
                        eligibility_response = requests.get(
                            f"{API_BASE_URL}/tournaments/1/eligibility/{team_id}",
                            headers=headers
                        )
                        
                        if eligibility_response.status_code == 200:
                            eligibility = eligibility_response.json()
                            print(f"  Eligibility: {eligibility}")
                        else:
                            print(f"  Eligibility check failed: {eligibility_response.status_code}")
                    else:
                        print("  No teams found")
                else:
                    print(f"  Failed to get teams: {teams_response.status_code}")
            else:
                print(f"  Failed to get user info: {me_response.status_code}")
        else:
            print(f"  Login failed: {response.status_code}")
    except Exception as e:
        print(f"  Error: {str(e)}")

if __name__ == "__main__":
    check_tournament_categories()
    check_all_tournaments()
    test_team_eligibility_quick()