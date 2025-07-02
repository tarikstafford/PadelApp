#!/usr/bin/env python3
"""
Script to create tournament test data:
- 64 players (users)
- 32 teams (2 players each)
- Register all teams for a tournament

This script tests the complete flow from user creation to tournament registration.
"""

import requests
import json
import random
import time
from typing import Dict, List, Optional

# Configuration
API_BASE_URL = "https://padelgo-backend-production.up.railway.app/api/v1"
# API_BASE_URL = "http://localhost:8000/api/v1"  # Use for local testing

# Test data configuration
NUM_PLAYERS = 64
NUM_TEAMS = 32
TOURNAMENT_ID = 1  # Assuming tournament ID 1 exists

class TournamentDataCreator:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.created_users = []
        self.created_teams = []
        self.admin_token = None
        
    def log(self, message: str):
        """Log with timestamp"""
        print(f"[{time.strftime('%H:%M:%S')}] {message}")
        
    def create_admin_user(self) -> Optional[str]:
        """Create an admin user and get auth token"""
        self.log("Creating admin user...")
        
        admin_data = {
            "full_name": "Tournament Admin",
            "email": "admin@tournament.test",
            "password": "admin123"
        }
        
        try:
            # Try to register admin
            response = self.session.post(
                f"{self.base_url}/auth/register",
                json=admin_data
            )
            
            if response.status_code == 201:
                data = response.json()
                self.admin_token = data.get("access_token")
                self.log("✓ Admin user created and logged in")
                return self.admin_token
            elif response.status_code == 400 and "already registered" in response.text:
                # Admin already exists, try to login
                self.log("Admin user already exists, attempting login...")
                return self.login_admin(admin_data["email"], admin_data["password"])
            else:
                self.log(f"✗ Failed to create admin: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.log(f"✗ Error creating admin: {str(e)}")
            return None
    
    def login_admin(self, email: str, password: str) -> Optional[str]:
        """Login existing admin user"""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json={"email": email, "password": password}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("access_token")
                self.log("✓ Admin logged in successfully")
                return self.admin_token
            else:
                self.log(f"✗ Failed to login admin: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.log(f"✗ Error logging in admin: {str(e)}")
            return None
    
    def create_player(self, player_num: int) -> Optional[Dict]:
        """Create a single player/user"""
        player_data = {
            "full_name": f"Player {player_num}",
            "email": f"player{player_num}@tournament.test",
            "password": "player123"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/auth/register",
                json=player_data
            )
            
            if response.status_code == 201:
                data = response.json()
                user_info = {
                    "id": data.get("user", {}).get("id"),
                    "email": player_data["email"],
                    "name": player_data["full_name"],
                    "token": data.get("access_token"),
                    "player_num": player_num
                }
                self.created_users.append(user_info)
                return user_info
            elif response.status_code == 400 and "already registered" in response.text:
                # User already exists, try to login
                return self.login_player(player_data["email"], player_data["password"], player_num)
            else:
                self.log(f"✗ Failed to create player {player_num}: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.log(f"✗ Error creating player {player_num}: {str(e)}")
            return None
    
    def login_player(self, email: str, password: str, player_num: int) -> Optional[Dict]:
        """Login existing player"""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json={"email": email, "password": password}
            )
            
            if response.status_code == 200:
                data = response.json()
                user_info = {
                    "id": data.get("user", {}).get("id"),
                    "email": email,
                    "name": f"Player {player_num}",
                    "token": data.get("access_token"),
                    "player_num": player_num
                }
                self.created_users.append(user_info)
                return user_info
            else:
                self.log(f"✗ Failed to login player {player_num}: {response.status_code}")
                return None
                
        except Exception as e:
            self.log(f"✗ Error logging in player {player_num}: {str(e)}")
            return None
    
    def create_players(self) -> List[Dict]:
        """Create all players"""
        self.log(f"Creating {NUM_PLAYERS} players...")
        
        for i in range(1, NUM_PLAYERS + 1):
            player = self.create_player(i)
            if player:
                if i % 10 == 0:
                    self.log(f"✓ Created {i}/{NUM_PLAYERS} players")
            time.sleep(0.1)  # Rate limiting
        
        self.log(f"✓ Total players created: {len(self.created_users)}")
        return self.created_users
    
    def create_team(self, team_num: int, player1: Dict, player2: Dict) -> Optional[Dict]:
        """Create a team with two players"""
        team_name = f"Team {team_num} ({player1['name'].split()[1]}-{player2['name'].split()[1]})"
        
        # Use player1's token to create the team
        headers = {
            "Authorization": f"Bearer {player1['token']}",
            "Content-Type": "application/json"
        }
        
        team_data = {
            "name": team_name
        }
        
        try:
            # Step 1: Create the team (player1 will be automatically added)
            response = self.session.post(
                f"{self.base_url}/users/me/teams",
                json=team_data,
                headers=headers
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                team_id = data.get("id")
                
                # Step 2: Add player2 to the team
                add_player_data = {"user_id": player2['id']}
                add_response = self.session.post(
                    f"{self.base_url}/users/me/teams/{team_id}/players",
                    json=add_player_data,
                    headers=headers
                )
                
                if add_response.status_code in [200, 201]:
                    team_info = {
                        "id": team_id,
                        "name": team_name,
                        "players": [player1, player2],
                        "creator_token": player1['token'],
                        "team_num": team_num
                    }
                    self.created_teams.append(team_info)
                    return team_info
                else:
                    self.log(f"✗ Failed to add player2 to team {team_num}: {add_response.status_code} - {add_response.text}")
                    # Still return the team with just one player
                    team_info = {
                        "id": team_id,
                        "name": team_name,
                        "players": [player1],
                        "creator_token": player1['token'],
                        "team_num": team_num
                    }
                    self.created_teams.append(team_info)
                    return team_info
            else:
                self.log(f"✗ Failed to create team {team_num}: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.log(f"✗ Error creating team {team_num}: {str(e)}")
            return None
    
    def create_teams(self) -> List[Dict]:
        """Create all teams by pairing players"""
        self.log(f"Creating {NUM_TEAMS} teams...")
        
        if len(self.created_users) < NUM_PLAYERS:
            self.log(f"✗ Not enough players created. Have {len(self.created_users)}, need {NUM_PLAYERS}")
            return []
        
        # Pair players into teams
        for i in range(NUM_TEAMS):
            player1 = self.created_users[i * 2]
            player2 = self.created_users[i * 2 + 1]
            
            team = self.create_team(i + 1, player1, player2)
            if team:
                if (i + 1) % 5 == 0:
                    self.log(f"✓ Created {i + 1}/{NUM_TEAMS} teams")
            time.sleep(0.1)  # Rate limiting
        
        self.log(f"✓ Total teams created: {len(self.created_teams)}")
        return self.created_teams
    
    def get_tournament_info(self) -> Optional[Dict]:
        """Get information about the tournament"""
        try:
            response = self.session.get(f"{self.base_url}/tournaments/{TOURNAMENT_ID}")
            
            if response.status_code == 200:
                return response.json()
            else:
                self.log(f"✗ Failed to get tournament info: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.log(f"✗ Error getting tournament info: {str(e)}")
            return None
    
    def register_team_for_tournament(self, team: Dict) -> bool:
        """Register a team for the tournament"""
        headers = {
            "Authorization": f"Bearer {team['creator_token']}",
            "Content-Type": "application/json"
        }
        
        # First, check team eligibility
        try:
            eligibility_response = self.session.get(
                f"{self.base_url}/tournaments/{TOURNAMENT_ID}/eligibility/{team['id']}",
                headers=headers
            )
            
            if eligibility_response.status_code != 200:
                self.log(f"✗ Could not check eligibility for team {team['name']}")
                return False
            
            eligibility = eligibility_response.json()
            if not eligibility.get("eligible", False):
                self.log(f"✗ Team {team['name']} is not eligible for tournament")
                return False
            
            # Get eligible categories
            eligible_categories = eligibility.get("eligible_categories", [])
            if not eligible_categories:
                self.log(f"✗ Team {team['name']} has no eligible categories")
                return False
            
            # Choose first eligible category
            category = eligible_categories[0]
            
            # Register for tournament
            registration_data = {
                "team_id": team['id'],
                "category": category
            }
            
            response = self.session.post(
                f"{self.base_url}/tournaments/{TOURNAMENT_ID}/register",
                json=registration_data,
                headers=headers
            )
            
            if response.status_code in [200, 201]:
                self.log(f"✓ Team {team['name']} registered for tournament in {category} category")
                return True
            else:
                self.log(f"✗ Failed to register team {team['name']}: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log(f"✗ Error registering team {team['name']}: {str(e)}")
            return False
    
    def register_all_teams(self) -> int:
        """Register all teams for the tournament"""
        self.log(f"Registering {len(self.created_teams)} teams for tournament {TOURNAMENT_ID}...")
        
        successful_registrations = 0
        
        for i, team in enumerate(self.created_teams):
            if self.register_team_for_tournament(team):
                successful_registrations += 1
            
            if (i + 1) % 5 == 0:
                self.log(f"✓ Processed {i + 1}/{len(self.created_teams)} team registrations")
            
            time.sleep(0.2)  # Rate limiting
        
        self.log(f"✓ Successfully registered {successful_registrations}/{len(self.created_teams)} teams")
        return successful_registrations
    
    def run_full_test(self):
        """Run the complete test scenario"""
        self.log("=" * 50)
        self.log("STARTING TOURNAMENT DATA CREATION")
        self.log("=" * 50)
        
        # Step 1: Create admin user
        if not self.create_admin_user():
            self.log("✗ Failed to create admin user. Aborting.")
            return
        
        # Step 2: Get tournament information
        tournament_info = self.get_tournament_info()
        if tournament_info:
            self.log(f"✓ Tournament found: {tournament_info.get('name', 'Unknown')}")
            self.log(f"  Status: {tournament_info.get('status', 'Unknown')}")
            self.log(f"  Max participants: {tournament_info.get('max_participants', 'Unknown')}")
        else:
            self.log("⚠ Could not get tournament info, but continuing...")
        
        # Step 3: Create players
        players = self.create_players()
        if len(players) < NUM_PLAYERS:
            self.log(f"⚠ Only created {len(players)}/{NUM_PLAYERS} players")
        
        # Step 4: Create teams
        teams = self.create_teams()
        if len(teams) < NUM_TEAMS:
            self.log(f"⚠ Only created {len(teams)}/{NUM_TEAMS} teams")
        
        # Step 5: Register teams for tournament
        if teams:
            registered_count = self.register_all_teams()
            
            self.log("=" * 50)
            self.log("SUMMARY")
            self.log("=" * 50)
            self.log(f"Players created: {len(players)}/{NUM_PLAYERS}")
            self.log(f"Teams created: {len(teams)}/{NUM_TEAMS}")
            self.log(f"Teams registered: {registered_count}/{len(teams)}")
            
            if registered_count > 0:
                self.log("✓ SUCCESS: Tournament data created successfully!")
            else:
                self.log("✗ FAILURE: No teams were registered for the tournament")
        else:
            self.log("✗ FAILURE: No teams created, cannot register for tournament")
    
    def cleanup_test_data(self):
        """Clean up test data (optional - implement if needed)"""
        self.log("Note: Cleanup not implemented. Test data will remain in database.")
        self.log("Test users have emails like: player1@tournament.test, player2@tournament.test, etc.")

def main():
    """Main function to run the script"""
    creator = TournamentDataCreator(API_BASE_URL)
    
    try:
        creator.run_full_test()
    except KeyboardInterrupt:
        creator.log("\n✗ Script interrupted by user")
    except Exception as e:
        creator.log(f"\n✗ Unexpected error: {str(e)}")
    finally:
        creator.log("\nScript completed.")

if __name__ == "__main__":
    main()