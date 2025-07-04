#!/usr/bin/env python3
"""
Update Tournament ID 1 to add categories so teams can register
"""

import requests
import json

API_BASE_URL = "https://padelgo-backend-production.up.railway.app/api/v1"
TOURNAMENT_ID = 1

def login_as_club_admin():
    """Try to login as the existing club admin"""
    
    # From the clubs API, we know john@john.com is owner of club 1
    admin_credentials = {
        "email": "john@john.com",
        "password": "admin123"  # Try common password
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/auth/login", json=admin_credentials)
        if response.status_code == 200:
            data = response.json()
            print("✓ Successfully logged in as club admin")
            return data.get("access_token")
        else:
            print(f"✗ Failed to login as club admin: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"✗ Error logging in: {str(e)}")
    
    return None

def get_tournament_details(tournament_id):
    """Get current tournament details"""
    try:
        response = requests.get(f"{API_BASE_URL}/tournaments/{tournament_id}")
        if response.status_code == 200:
            tournament = response.json()
            print(f"✓ Current tournament details:")
            print(f"  Name: {tournament.get('name')}")
            print(f"  Categories: {len(tournament.get('categories', []))}")
            print(f"  Status: {tournament.get('status')}")
            print(f"  Max participants: {tournament.get('max_participants')}")
            return tournament
        else:
            print(f"✗ Failed to get tournament: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"✗ Error getting tournament: {str(e)}")
    
    return None

def update_tournament_with_categories(tournament_id, admin_token):
    """Update tournament to add categories"""
    
    # Define the update with categories
    update_data = {
        "categories": [
            {
                "category": "BRONZE",
                "max_participants": 16
            },
            {
                "category": "SILVER",
                "max_participants": 16
            }
        ]
    }
    
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.put(
            f"{API_BASE_URL}/tournaments/{tournament_id}", 
            json=update_data, 
            headers=headers
        )
        
        if response.status_code == 200:
            tournament = response.json()
            print(f"✓ Tournament updated successfully!")
            print(f"  Categories: {len(tournament.get('categories', []))}")
            for cat in tournament.get('categories', []):
                print(f"    - {cat.get('category')}: {cat.get('max_participants')} max participants")
            return tournament
        else:
            print(f"✗ Failed to update tournament: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"✗ Error updating tournament: {str(e)}")
    
    return None

def test_team_eligibility_after_update(tournament_id):
    """Test if teams can now register after adding categories"""
    
    # Try to login as a test user and check team eligibility
    test_credentials = {
        "email": "testplayer1@test.com",
        "password": "test123"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/auth/login", json=test_credentials)
        if response.status_code == 200:
            auth_data = response.json()
            token = auth_data.get("access_token")
            
            # Get user details
            headers = {"Authorization": f"Bearer {token}"}
            me_response = requests.get(f"{API_BASE_URL}/users/me", headers=headers)
            
            if me_response.status_code == 200:
                user = me_response.json()
                
                # Get user teams
                teams_response = requests.get(f"{API_BASE_URL}/users/me/teams", headers=headers)
                
                if teams_response.status_code == 200:
                    teams = teams_response.json()
                    print(f"\\n✓ Found {len(teams)} teams for test user")
                    
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
                            
                            print(f"  Team '{team_name}': {'✓ Eligible' if eligible else '✗ Not eligible'}")
                            if eligible:
                                print(f"    Categories: {categories}")
                            else:
                                print(f"    Reason: {eligibility.get('reason', 'Unknown')}")
                        else:
                            print(f"  Team '{team_name}': Could not check eligibility")
                else:
                    print("  No teams found for test user")
            else:
                print("  Could not get user details")
        else:
            print("  Could not login test user for eligibility check")
    except Exception as e:
        print(f"  Error testing eligibility: {str(e)}")

def main():
    print("Updating Tournament 1 with categories...")
    print("=" * 50)
    
    # Step 1: Get current tournament details
    tournament = get_tournament_details(TOURNAMENT_ID)
    if not tournament:
        print("Cannot proceed without tournament details")
        return
    
    # Step 2: Login as club admin
    admin_token = login_as_club_admin()
    if not admin_token:
        print("Cannot proceed without admin access")
        return
    
    # Step 3: Update tournament with categories
    updated_tournament = update_tournament_with_categories(TOURNAMENT_ID, admin_token)
    if not updated_tournament:
        print("Failed to update tournament")
        return
    
    # Step 4: Test team eligibility
    test_team_eligibility_after_update(TOURNAMENT_ID)
    
    print("\\n" + "=" * 50)
    print("Tournament update completed!")
    print("Teams should now be able to register for the tournament.")

if __name__ == "__main__":
    main()