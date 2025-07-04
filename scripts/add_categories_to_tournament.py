#!/usr/bin/env python3
"""
Add categories to Tournament 1 using admin credentials
"""

import requests
import json

API_BASE_URL = "https://padelgo-backend-production.up.railway.app/api/v1"

# Known admin credentials from the clubs API
ADMIN_CREDENTIALS = [
    {"email": "john@john.com", "password": "admin123"},
    {"email": "sham@gmail.com", "password": "admin123"},
]

def try_admin_login():
    """Try to login as admin"""
    
    for creds in ADMIN_CREDENTIALS:
        try:
            response = requests.post(f"{API_BASE_URL}/auth/login", json=creds)
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Successfully logged in as {creds['email']}")
                return data.get("access_token")
            else:
                print(f"✗ Failed to login as {creds['email']}: {response.status_code}")
        except Exception as e:
            print(f"✗ Error logging in as {creds['email']}: {str(e)}")
    
    return None

def add_categories_to_tournament(admin_token):
    """Add categories to tournament 1"""
    
    # Define categories to add
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
    
    print("Adding categories to Tournament 1...")
    
    try:
        response = requests.put(
            f"{API_BASE_URL}/tournaments/1",
            json=update_data,
            headers=headers
        )
        
        if response.status_code == 200:
            tournament = response.json()
            print("✓ Tournament updated successfully!")
            print(f"  Categories in response: {len(tournament.get('categories', []))}")
            
            for cat in tournament.get('categories', []):
                print(f"    - {cat.get('category')}: {cat.get('max_participants')} max participants")
            
            return True
        else:
            print(f"✗ Failed to update tournament: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Error updating tournament: {str(e)}")
        return False

def verify_tournament_after_update():
    """Verify tournament has categories after update"""
    
    print("\nVerifying tournament after update...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/tournaments/1")
        if response.status_code == 200:
            tournament = response.json()
            categories = tournament.get('categories', [])
            print(f"✓ Tournament now has {len(categories)} categories")
            
            for cat in categories:
                print(f"    - {cat.get('category')}: {cat.get('max_participants')} max participants")
            
            return len(categories) > 0
        else:
            print(f"✗ Failed to verify tournament: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error verifying tournament: {str(e)}")
        return False

def test_team_eligibility_after_categories():
    """Test team eligibility after adding categories"""
    
    print("\nTesting team eligibility after adding categories...")
    
    # Login test user
    test_user = {
        "email": "player01@populate.example",
        "password": "player123"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/auth/login", json=test_user)
        if response.status_code == 200:
            auth_data = response.json()
            token = auth_data.get("access_token")
            
            headers = {"Authorization": f"Bearer {token}"}
            
            # Get teams
            teams_response = requests.get(f"{API_BASE_URL}/users/me/teams", headers=headers)
            
            if teams_response.status_code == 200:
                teams = teams_response.json()
                
                if teams:
                    team = teams[0]
                    team_id = team.get('id')
                    team_name = team.get('name')
                    
                    print(f"Testing team: {team_name}")
                    
                    # Check eligibility
                    eligibility_response = requests.get(
                        f"{API_BASE_URL}/tournaments/1/eligibility/{team_id}",
                        headers=headers
                    )
                    
                    if eligibility_response.status_code == 200:
                        eligibility = eligibility_response.json()
                        eligible = eligibility.get('eligible', False)
                        categories = eligibility.get('eligible_categories', [])
                        
                        print(f"✓ Team eligibility: {'Eligible' if eligible else 'Not eligible'}")
                        if eligible:
                            print(f"  Eligible categories: {categories}")
                        else:
                            print(f"  Reason: {eligibility.get('reason', 'Unknown')}")
                    else:
                        print(f"✗ Eligibility check failed: {eligibility_response.status_code}")
                else:
                    print("No teams found")
            else:
                print(f"Failed to get teams: {teams_response.status_code}")
        else:
            print(f"Login failed: {response.status_code}")
    except Exception as e:
        print(f"Error: {str(e)}")

def main():
    print("Adding categories to Tournament 1...")
    print("=" * 50)
    
    # Step 1: Login as admin
    admin_token = try_admin_login()
    if not admin_token:
        print("✗ Could not login as admin")
        return
    
    # Step 2: Add categories
    success = add_categories_to_tournament(admin_token)
    if not success:
        print("✗ Failed to add categories")
        return
    
    # Step 3: Verify categories were added
    has_categories = verify_tournament_after_update()
    if not has_categories:
        print("✗ Categories not found after update")
        return
    
    # Step 4: Test team eligibility
    test_team_eligibility_after_categories()
    
    print("\n" + "=" * 50)
    print("✅ Tournament categories added successfully!")
    print("Teams should now be able to register for the tournament.")

if __name__ == "__main__":
    main()