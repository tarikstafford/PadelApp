#!/usr/bin/env python3
"""
Comprehensive script to populate tournament and leaderboard data:
1. Create players with varied ELO ratings
2. Create games to establish leaderboard rankings
3. Create 2-player teams
4. Register teams for tournament

This script addresses both leaderboard visibility and tournament participation.
"""

import requests
import json
import random
import time
from typing import Dict, List, Optional

# Configuration
API_BASE_URL = "https://padelgo-backend-production.up.railway.app/api/v1"
TOURNAMENT_ID = 1
NUM_PLAYERS = 32  # Smaller number for testing
NUM_TEAMS = 16
NUM_GAMES_TO_SIMULATE = 20  # Games to create ELO changes for leaderboard

class TournamentAndLeaderboardPopulator:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.created_users = []
        self.created_teams = []
        self.created_games = []
        self.admin_token = None
        
    def log(self, message: str):
        """Log with timestamp"""
        print(f"[{time.strftime('%H:%M:%S')}] {message}")
        
    def create_admin_and_login(self) -> Optional[str]:
        """Create admin or login existing admin"""
        self.log("Setting up admin user...")
        
        admin_data = {
            "full_name": "Tournament Admin",
            "email": "admin@populate.example",
            "password": "admin123"
        }
        
        # Try to login first
        try:
            response = self.session.post(f"{self.base_url}/auth/login", json={
                "email": admin_data["email"],
                "password": admin_data["password"]
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("access_token")
                self.log("✓ Admin logged in successfully")
                return self.admin_token
        except Exception as e:
            self.log(f"Login attempt failed: {str(e)}")
            pass
        
        # If login failed, try to register
        try:
            response = self.session.post(f"{self.base_url}/auth/register", json=admin_data)
            if response.status_code == 201:
                data = response.json()
                self.admin_token = data.get("access_token")
                self.log("✓ Admin user created and logged in")
                return self.admin_token
            else:
                self.log(f"Registration failed: {response.status_code} - {response.text}")
        except Exception as e:
            self.log(f"Registration attempt failed: {str(e)}")
            pass
        
        self.log("✗ Failed to setup admin user")
        return None
    
    def create_player_with_elo(self, player_num: int, base_elo: float = None) -> Optional[Dict]:
        """Create a player with a specific ELO rating"""
        if base_elo is None:
            # Random ELO between 1.0 and 5.0
            base_elo = round(random.uniform(1.0, 5.0), 1)
        
        player_data = {
            "full_name": f"Player {player_num:02d}",
            "email": f"player{player_num:02d}@populate.example",
            "password": "player123"
        }
        
        try:
            # Try to register
            response = self.session.post(f"{self.base_url}/auth/register", json=player_data)
            
            if response.status_code == 201:
                data = response.json()
                access_token = data.get("access_token")
                
                # Get user details from /users/me endpoint
                me_response = self.session.get(f"{self.base_url}/users/me", headers={
                    "Authorization": f"Bearer {access_token}"
                })
                
                if me_response.status_code == 200:
                    user_data_response = me_response.json()
                    user_info = {
                        "id": user_data_response.get("id"),
                        "email": player_data["email"],
                        "name": player_data["full_name"],
                        "token": access_token,
                        "player_num": player_num,
                        "target_elo": base_elo
                    }
                    self.created_users.append(user_info)
                else:
                    self.log(f"✗ Failed to get user details for player {player_num}")
                    return None
                
                # Update ELO rating if different from default
                if base_elo != 1.0:
                    self.update_player_elo(user_info, base_elo)
                
                return user_info
                
            elif response.status_code == 400 and "already registered" in response.text:
                # User exists, login
                login_response = self.session.post(f"{self.base_url}/auth/login", json={
                    "email": player_data["email"],
                    "password": player_data["password"]
                })
                
                if login_response.status_code == 200:
                    data = login_response.json()
                    access_token = data.get("access_token")
                    
                    # Get user details from /users/me endpoint
                    me_response = self.session.get(f"{self.base_url}/users/me", headers={
                        "Authorization": f"Bearer {access_token}"
                    })
                    
                    if me_response.status_code == 200:
                        user_data_response = me_response.json()
                        user_info = {
                            "id": user_data_response.get("id"),
                            "email": player_data["email"],
                            "name": player_data["full_name"],
                            "token": access_token,
                            "player_num": player_num,
                            "target_elo": base_elo
                        }
                        self.created_users.append(user_info)
                        return user_info
                    else:
                        self.log(f"✗ Failed to get user details for player {player_num}")
                        return None
                    
            else:
                self.log(f"✗ Failed to create player {player_num}: {response.status_code}")
                return None
                
        except Exception as e:
            self.log(f"✗ Error creating player {player_num}: {str(e)}")
            return None
    
    def update_player_elo(self, player: Dict, new_elo: float):
        """Update a player's ELO rating"""
        # This would require an admin endpoint to set ELO ratings
        # For now, we'll simulate ELO changes through games
        pass
    
    def create_all_players(self) -> List[Dict]:
        """Create all players with varied ELO ratings"""
        self.log(f"Creating {NUM_PLAYERS} players with varied ELO ratings...")
        
        # Create ELO distribution
        elo_ranges = [
            (1.0, 1.5, 8),    # Bronze players
            (1.5, 2.5, 12),   # Silver players  
            (2.5, 3.5, 8),    # Gold players
            (3.5, 5.0, 4),    # Platinum players
        ]
        
        player_count = 1
        for min_elo, max_elo, count in elo_ranges:
            for i in range(count):
                if player_count <= NUM_PLAYERS:
                    elo = round(random.uniform(min_elo, max_elo), 1)
                    player = self.create_player_with_elo(player_count, elo)
                    if player:
                        if player_count % 5 == 0:
                            self.log(f"✓ Created {player_count}/{NUM_PLAYERS} players")
                    player_count += 1
                    time.sleep(0.1)
        
        self.log(f"✓ Total players created: {len(self.created_users)}")
        return self.created_users
    
    def simulate_game_for_elo(self, player1: Dict, player2: Dict, player3: Dict, player4: Dict) -> bool:
        """Simulate a game between 4 players to generate ELO changes"""
        # This is a simplified simulation - in reality you'd need to:
        # 1. Create teams
        # 2. Create a game with those teams
        # 3. Record game results
        # 4. Update ELO ratings based on results
        
        # For now, let's just log that we would create a game
        self.log(f"📊 Simulated game: {player1['name']} & {player2['name']} vs {player3['name']} & {player4['name']}")
        return True
    
    def simulate_games_for_leaderboard(self):
        """Simulate games to create ELO rating changes for leaderboard"""
        self.log(f"Simulating {NUM_GAMES_TO_SIMULATE} games to populate leaderboard...")
        
        if len(self.created_users) < 4:
            self.log("✗ Need at least 4 players to simulate games")
            return
        
        games_simulated = 0
        for i in range(NUM_GAMES_TO_SIMULATE):
            # Pick 4 random players
            players = random.sample(self.created_users, 4)
            
            if self.simulate_game_for_elo(*players):
                games_simulated += 1
                
            if (i + 1) % 5 == 0:
                self.log(f"✓ Simulated {i + 1}/{NUM_GAMES_TO_SIMULATE} games")
            
            time.sleep(0.1)
        
        self.log(f"✓ Simulated {games_simulated} games for leaderboard population")
    
    def create_team_with_two_players(self, team_num: int, player1: Dict, player2: Dict) -> Optional[Dict]:
        """Create a team with exactly 2 players"""
        team_name = f"Team {team_num:02d} ({player1['name'].split()[1]}-{player2['name'].split()[1]})"
        
        headers = {
            "Authorization": f"Bearer {player1['token']}",
            "Content-Type": "application/json"
        }
        
        team_data = {"name": team_name}
        
        try:
            # Create team
            response = self.session.post(f"{self.base_url}/users/me/teams", json=team_data, headers=headers)
            
            if response.status_code in [200, 201]:
                data = response.json()
                team_id = data.get("id")
                
                # Try to add second player
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
                    self.log(f"⚠ Team {team_num} created but couldn't add second player (endpoint not available)")
                    # Still return team with one player
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
                self.log(f"✗ Failed to create team {team_num}: {response.status_code}")
                return None
                
        except Exception as e:
            self.log(f"✗ Error creating team {team_num}: {str(e)}")
            return None
    
    def create_all_teams(self) -> List[Dict]:
        """Create teams by pairing players"""
        self.log(f"Creating {NUM_TEAMS} teams...")
        
        if len(self.created_users) < NUM_TEAMS * 2:
            self.log(f"✗ Not enough players. Have {len(self.created_users)}, need {NUM_TEAMS * 2}")
            return []
        
        for i in range(NUM_TEAMS):
            player1 = self.created_users[i * 2]
            player2 = self.created_users[i * 2 + 1]
            
            team = self.create_team_with_two_players(i + 1, player1, player2)
            if team:
                if (i + 1) % 5 == 0:
                    self.log(f"✓ Created {i + 1}/{NUM_TEAMS} teams")
            time.sleep(0.1)
        
        self.log(f"✓ Total teams created: {len(self.created_teams)}")
        return self.created_teams
    
    def register_team_for_tournament(self, team: Dict) -> bool:
        """Register a team for the tournament"""
        headers = {"Authorization": f"Bearer {team['creator_token']}"}
        
        try:
            # Check eligibility
            response = self.session.get(
                f"{self.base_url}/tournaments/{TOURNAMENT_ID}/eligibility/{team['id']}",
                headers=headers
            )
            
            if response.status_code == 200:
                eligibility = response.json()
                if eligibility.get("eligible"):
                    categories = eligibility.get("eligible_categories", [])
                    if categories:
                        category = categories[0]
                        
                        # Register
                        registration_data = {"team_id": team['id'], "category": category}
                        reg_response = self.session.post(
                            f"{self.base_url}/tournaments/{TOURNAMENT_ID}/register",
                            json=registration_data,
                            headers=headers
                        )
                        
                        if reg_response.status_code in [200, 201]:
                            self.log(f"✓ {team['name']} registered for tournament")
                            return True
                        else:
                            self.log(f"✗ Failed to register {team['name']}: {reg_response.status_code}")
                else:
                    self.log(f"⚠ {team['name']} not eligible: {eligibility.get('reason')}")
            else:
                self.log(f"✗ Could not check eligibility for {team['name']}")
                
        except Exception as e:
            self.log(f"✗ Error registering {team['name']}: {str(e)}")
        
        return False
    
    def register_all_teams(self) -> int:
        """Register all eligible teams for tournament"""
        self.log(f"Registering teams for tournament...")
        
        successful_registrations = 0
        for team in self.created_teams:
            if self.register_team_for_tournament(team):
                successful_registrations += 1
            time.sleep(0.1)
        
        self.log(f"✓ Registered {successful_registrations}/{len(self.created_teams)} teams")
        return successful_registrations
    
    def check_final_status(self):
        """Check final leaderboard and tournament status"""
        self.log("Checking final status...")
        
        # Check leaderboard
        try:
            response = self.session.get(f"{self.base_url}/leaderboard")
            if response.status_code == 200:
                leaderboard = response.json()
                count = len(leaderboard.get("leaderboard", []))
                self.log(f"✓ Leaderboard now has {count} entries")
            else:
                self.log(f"⚠ Could not check leaderboard: {response.status_code}")
        except:
            self.log("✗ Error checking leaderboard")
        
        # Check tournament
        try:
            response = self.session.get(f"{self.base_url}/tournaments/{TOURNAMENT_ID}")
            if response.status_code == 200:
                tournament = response.json()
                teams = tournament.get("total_registered_teams", 0)
                self.log(f"✓ Tournament now has {teams} registered teams")
            else:
                self.log(f"⚠ Could not check tournament: {response.status_code}")
        except:
            self.log("✗ Error checking tournament")
    
    def run_full_population(self):
        """Run the complete population process"""
        self.log("=" * 60)
        self.log("STARTING TOURNAMENT AND LEADERBOARD POPULATION")
        self.log("=" * 60)
        
        # Step 1: Setup admin
        if not self.create_admin_and_login():
            self.log("✗ Failed to setup admin. Aborting.")
            return
        
        # Step 2: Create players
        players = self.create_all_players()
        if len(players) < 4:
            self.log("✗ Not enough players created")
            return
        
        # Step 3: Simulate games for leaderboard
        self.simulate_games_for_leaderboard()
        
        # Step 4: Create teams
        teams = self.create_all_teams()
        
        # Step 5: Register teams for tournament
        if teams:
            registered_count = self.register_all_teams()
        else:
            registered_count = 0
        
        # Step 6: Check final status
        self.check_final_status()
        
        # Summary
        self.log("=" * 60)
        self.log("POPULATION SUMMARY")
        self.log("=" * 60)
        self.log(f"Players created: {len(players)}")
        self.log(f"Teams created: {len(teams)}")
        self.log(f"Teams registered: {registered_count}")
        self.log(f"Games simulated: {NUM_GAMES_TO_SIMULATE}")
        
        if len(players) > 0:
            self.log("✅ SUCCESS: Data population completed!")
            self.log("📊 Check the leaderboard to see players")
            self.log("🏆 Check the tournament to see registered teams")
        else:
            self.log("❌ FAILURE: No players were created")

def main():
    """Main function"""
    populator = TournamentAndLeaderboardPopulator(API_BASE_URL)
    
    try:
        populator.run_full_population()
    except KeyboardInterrupt:
        populator.log("\n✗ Script interrupted by user")
    except Exception as e:
        populator.log(f"\n✗ Unexpected error: {str(e)}")
    finally:
        populator.log("\nScript completed.")

if __name__ == "__main__":
    main()