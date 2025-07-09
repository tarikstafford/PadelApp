#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, '/Users/tarikstafford/Desktop/Projects/PadelApp/padel-app/apps/api')

from app.database import get_db
from app.crud.game_score_crud import game_score_crud
from app.models import Game

def test_score_access():
    db = next(get_db())
    try:
        print("Testing score access for game ID 6...")
        
        # Test get_user_team_for_game with a test user ID (adjust as needed)
        test_user_id = 1  # Change this to a valid user ID
        game_id = 6
        
        # First check if game exists
        game = db.query(Game).filter(Game.id == game_id).first()
        if not game:
            print(f"Game {game_id} not found!")
            return
            
        print(f"Game found: ID={game.id}, Status={game.game_status}")
        print(f"Teams assigned: team1_id={game.team1_id}, team2_id={game.team2_id}")
        print(f"Number of players: {len(game.players) if game.players else 0}")
        
        # Test the get_user_team_for_game function
        user_team = game_score_crud.get_user_team_for_game(db, game_id, test_user_id)
        print(f"\nUser {test_user_id} team assignment: {user_team}")
        
        if user_team is None:
            print("User is NOT a participant")
        elif user_team == -1:
            print("User IS a participant but teams not assigned yet")
        else:
            print(f"User is on team {user_team}")
            
        # Test can_submit_score
        can_submit, message = game_score_crud.can_submit_score(db, game_id, test_user_id)
        print(f"\nCan submit score: {can_submit}")
        print(f"Message: {message}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == '__main__':
    test_score_access()