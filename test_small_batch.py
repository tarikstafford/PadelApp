#!/usr/bin/env python3
"""
Create a small batch of test data to verify the flow works
Creates 4 players and 2 teams (when the add player endpoint is available)
"""

import requests
import json
import time

API_BASE_URL = "https://padelgo-backend-production.up.railway.app/api/v1"
TOURNAMENT_ID = 1

def create_small_batch():
    print("Creating small batch of test data...")
    
    # Create 4 players
    players = []
    for i in range(1, 5):
        print(f"Creating player {i}...")
        
        user_data = {
            "full_name": f"Batch Player {i}",
            "email": f"batchplayer{i}@test.com", 
            "password": "test123"
        }
        
        try:
            response = requests.post(f"{API_BASE_URL}/auth/register", json=user_data)
            if response.status_code == 201:
                auth_data = response.json()
                player_info = {
                    "id": auth_data.get("user", {}).get("id"),
                    "token": auth_data.get("access_token"),
                    "email": user_data["email"],
                    "name": user_data["full_name"],
                    "player_num": i
                }
                players.append(player_info)
                print(f"✓ Player {i} created")
            elif response.status_code == 400 and "already registered" in response.text:
                # Login existing user
                login_response = requests.post(f"{API_BASE_URL}/auth/login", json={
                    "email": user_data["email"],
                    "password": user_data["password"]
                })
                if login_response.status_code == 200:
                    auth_data = login_response.json()
                    player_info = {
                        "id": auth_data.get("user", {}).get("id"),
                        "token": auth_data.get("access_token"),
                        "email": user_data["email"],
                        "name": user_data["full_name"],
                        "player_num": i
                    }
                    players.append(player_info)
                    print(f"✓ Player {i} logged in")
                else:
                    print(f"✗ Failed to login player {i}")
            else:
                print(f"✗ Failed to create player {i}: {response.status_code}")
                
        except Exception as e:
            print(f"✗ Error with player {i}: {str(e)}")
        
        time.sleep(0.1)  # Rate limiting
    
    print(f"\n✓ Created {len(players)} players")
    
    # Create 2 teams
    teams = []
    for team_num in range(1, 3):
        if len(players) >= team_num * 2:
            player1 = players[(team_num - 1) * 2]
            player2 = players[(team_num - 1) * 2 + 1]
            
            print(f"\nCreating team {team_num} with players {player1['player_num']} and {player2['player_num']}...")
            
            # Create team with player1
            headers = {"Authorization": f"Bearer {player1['token']}"}
            team_data = {"name": f"Batch Team {team_num}"}
            
            try:
                response = requests.post(f"{API_BASE_URL}/users/me/teams", json=team_data, headers=headers)
                if response.status_code in [200, 201]:
                    team_info = response.json()
                    team_id = team_info.get("id")
                    print(f"  ✓ Team created with ID: {team_id}")
                    
                    # Try to add player2 (will fail until endpoint is deployed)
                    add_player_data = {"user_id": player2['id']}
                    add_response = requests.post(
                        f"{API_BASE_URL}/users/me/teams/{team_id}/players",
                        json=add_player_data,
                        headers=headers
                    )
                    
                    if add_response.status_code in [200, 201]:
                        print(f"  ✓ Player {player2['player_num']} added to team")
                        team_players = [player1, player2]
                    else:
                        print(f"  ⚠ Failed to add player {player2['player_num']}: {add_response.status_code}")
                        print(f"    (This is expected until the endpoint is deployed)")
                        team_players = [player1]
                    
                    teams.append({
                        "id": team_id,
                        "name": f"Batch Team {team_num}",
                        "players": team_players,
                        "creator_token": player1['token']
                    })
                    
                else:
                    print(f"  ✗ Failed to create team {team_num}: {response.status_code}")
                    
            except Exception as e:
                print(f"  ✗ Error creating team {team_num}: {str(e)}")
        
        time.sleep(0.1)
    
    print(f"\n✓ Created {len(teams)} teams")
    
    # Test tournament registration with created teams
    print(f"\nTesting tournament registration...")
    for team in teams:
        team_name = team['name']
        team_id = team['id']
        headers = {"Authorization": f"Bearer {team['creator_token']}"}
        
        # Check eligibility
        try:
            response = requests.get(f"{API_BASE_URL}/tournaments/{TOURNAMENT_ID}/eligibility/{team_id}", headers=headers)
            if response.status_code == 200:
                eligibility = response.json()
                print(f"  {team_name}: {'Eligible' if eligibility.get('eligible') else 'Not eligible'}")
                if not eligibility.get('eligible'):
                    print(f"    Reason: {eligibility.get('reason', 'Unknown')}")
                else:
                    categories = eligibility.get('eligible_categories', [])
                    print(f"    Categories: {categories}")
            else:
                print(f"  {team_name}: Could not check eligibility ({response.status_code})")
        except Exception as e:
            print(f"  {team_name}: Error checking eligibility - {str(e)}")
    
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    print(f"Players created: {len(players)}")
    print(f"Teams created: {len(teams)}")
    print("Next steps:")
    print("1. Deploy backend with new team management endpoint")
    print("2. Run full script to create 64 players and 32 teams")
    print("3. Register teams for tournament")

if __name__ == "__main__":
    create_small_batch()