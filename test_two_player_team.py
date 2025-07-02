#!/usr/bin/env python3
"""
Test creating a 2-player team and registering for tournament
"""

import requests
import json

API_BASE_URL = "https://padelgo-backend-production.up.railway.app/api/v1"
TOURNAMENT_ID = 1

def test_two_player_team():
    print("Testing 2-player team creation and registration...")
    
    # Create two test users
    users = []
    for i in [1, 2]:
        print(f"\nCreating user {i}...")
        user_data = {
            "full_name": f"Test Player {i}",
            "email": f"testplayer{i}@test.com",
            "password": "test123"
        }
        
        response = requests.post(f"{API_BASE_URL}/auth/register", json=user_data)
        if response.status_code == 201:
            auth_data = response.json()
            access_token = auth_data.get("access_token")
            
            # Get user details from /users/me endpoint
            me_response = requests.get(f"{API_BASE_URL}/users/me", headers={
                "Authorization": f"Bearer {access_token}"
            })
            
            if me_response.status_code == 200:
                user_data_response = me_response.json()
                user_info = {
                    "id": user_data_response.get("id"),
                    "token": access_token,
                    "email": user_data["email"],
                    "name": user_data["full_name"]
                }
                users.append(user_info)
                print(f"✓ User {i} created with ID: {user_info['id']}")
            else:
                print(f"✗ Failed to get user details for user {i}")
                return
        elif response.status_code == 400 and "already registered" in response.text:
            # User exists, login
            login_response = requests.post(f"{API_BASE_URL}/auth/login", json={
                "email": user_data["email"], 
                "password": user_data["password"]
            })
            if login_response.status_code == 200:
                auth_data = login_response.json()
                access_token = auth_data.get("access_token")
                
                # Get user details from /users/me endpoint
                me_response = requests.get(f"{API_BASE_URL}/users/me", headers={
                    "Authorization": f"Bearer {access_token}"
                })
                
                if me_response.status_code == 200:
                    user_data_response = me_response.json()
                    user_info = {
                        "id": user_data_response.get("id"),
                        "token": access_token,
                        "email": user_data["email"],
                        "name": user_data["full_name"]
                    }
                    users.append(user_info)
                    print(f"✓ User {i} logged in with ID: {user_info['id']}")
                else:
                    print(f"✗ Failed to get user details for user {i}")
                    return
            else:
                print(f"✗ Failed to login user {i}")
                return
        else:
            print(f"✗ Failed to create user {i}: {response.status_code}")
            return
    
    if len(users) != 2:
        print("✗ Failed to create both users")
        return
    
    player1, player2 = users
    
    # Create team with player1
    print(f"\nCreating team with player1...")
    headers = {"Authorization": f"Bearer {player1['token']}"}
    team_data = {"name": "Test Two Player Team"}
    
    response = requests.post(f"{API_BASE_URL}/users/me/teams", json=team_data, headers=headers)
    if response.status_code in [200, 201]:
        team_info = response.json()
        team_id = team_info.get("id")
        print(f"✓ Team created with ID: {team_id}")
        print(f"  Current players: {len(team_info.get('players', []))}")
    else:
        print(f"✗ Failed to create team: {response.status_code} - {response.text}")
        return
    
    # Add player2 to the team
    print(f"\nAdding player2 to team...")
    add_player_data = {"user_id": player2['id']}
    response = requests.post(
        f"{API_BASE_URL}/users/me/teams/{team_id}/players", 
        json=add_player_data, 
        headers=headers
    )
    
    if response.status_code in [200, 201]:
        updated_team = response.json()
        print(f"✓ Player2 added to team")
        print(f"  Team now has {len(updated_team.get('players', []))} players")
    else:
        print(f"✗ Failed to add player2: {response.status_code} - {response.text}")
        print("Continuing with 1-player team...")
    
    # Check eligibility
    print(f"\nChecking team eligibility...")
    response = requests.get(f"{API_BASE_URL}/tournaments/{TOURNAMENT_ID}/eligibility/{team_id}", headers=headers)
    if response.status_code == 200:
        eligibility = response.json()
        print(f"✓ Eligibility: {eligibility}")
        
        if eligibility.get("eligible"):
            categories = eligibility.get("eligible_categories", [])
            if categories:
                category = categories[0]
                print(f"  Using category: {category}")
                
                # Register for tournament
                print(f"\nRegistering team for tournament...")
                registration_data = {"team_id": team_id, "category": category}
                response = requests.post(
                    f"{API_BASE_URL}/tournaments/{TOURNAMENT_ID}/register", 
                    json=registration_data, 
                    headers=headers
                )
                
                if response.status_code in [200, 201]:
                    print("✓ Team successfully registered for tournament!")
                else:
                    print(f"✗ Registration failed: {response.status_code} - {response.text}")
            else:
                print("✗ No eligible categories")
        else:
            print(f"✗ Team not eligible: {eligibility.get('reason', 'Unknown reason')}")
    else:
        print(f"✗ Failed to check eligibility: {response.status_code} - {response.text}")
    
    print("\n" + "="*50)
    print("Two-Player Team Test Complete")
    print("="*50)

if __name__ == "__main__":
    test_two_player_team()