#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, '/Users/tarikstafford/Desktop/Projects/PadelApp/padel-app/apps/api')

from app.database import get_db
from app.crud.game_crud import game_crud
from app.services.game_expiration_service import game_expiration_service
from app.models.game import Game, GameStatus
from app.models.user import User
import traceback

def simulate_api_call(game_id: int, user_id: int = 1):
    """Simulate the exact API call flow"""
    db = next(get_db())
    try:
        print(f"=== Simulating API call for game {game_id} with user {user_id} ===")
        
        # Step 1: Check expiration (same as API)
        print("\n1. Checking game expiration...")
        try:
            game_expiration_service.check_single_game_expiration(db, game_id)
            print("✓ Expiration check passed")
        except Exception as e:
            print(f"✗ Error in expiration check: {e}")
            print("Stack trace:")
            traceback.print_exc()
            raise
        
        # Step 2: Get game with eager loading (same as API)
        print("\n2. Getting game with eager loading...")
        try:
            game = game_crud.get_game(db, game_id=game_id)
            if not game:
                print("✗ Game not found")
                return
            print("✓ Game retrieved")
        except Exception as e:
            print(f"✗ Error getting game: {e}")
            print("Stack trace:")
            traceback.print_exc()
            raise
        
        # Step 3: Check authorization (simulate)
        print("\n3. Checking authorization...")
        try:
            # Get current user (simulate)
            current_user = db.query(User).filter(User.id == user_id).first()
            if not current_user:
                print(f"✗ User {user_id} not found")
                return
                
            is_participant = any(gp.user_id == current_user.id for gp in game.players)
            is_creator = game.booking and game.booking.user_id == current_user.id
            
            print(f"Is participant: {is_participant}")
            print(f"Is creator: {is_creator}")
            
            if not is_participant and not is_creator:
                print("✗ User not authorized")
            else:
                print("✓ User authorized")
        except Exception as e:
            print(f"✗ Error in authorization check: {e}")
            print("Stack trace:")
            traceback.print_exc()
            raise
        
        # Step 4: Return game data (simulate response)
        print("\n4. Preparing response...")
        try:
            # Try to access all the fields that would be serialized
            response_data = {
                "id": game.id,
                "club_id": game.club_id,
                "booking_id": game.booking_id,
                "game_type": game.game_type.value,
                "game_status": game.game_status.value,
                "skill_level": game.skill_level,
                "start_time": str(game.start_time),
                "end_time": str(game.end_time),
            }
            
            # Access booking data
            if game.booking:
                response_data["booking"] = {
                    "id": game.booking.id,
                    "court_id": game.booking.court_id,
                    "user_id": game.booking.user_id,
                }
                
                # Access court data
                if game.booking.court:
                    response_data["booking"]["court"] = {
                        "id": game.booking.court.id,
                        "name": game.booking.court.name,
                        "club_id": game.booking.court.club_id,
                    }
                    
                    # Access club data
                    if game.booking.court.club:
                        response_data["booking"]["court"]["club"] = {
                            "id": game.booking.court.club.id,
                            "name": game.booking.court.club.name,
                        }
            
            # Access players data
            response_data["players"] = []
            for player in game.players:
                player_data = {
                    "user_id": player.user_id,
                    "status": player.status.value,
                }
                if player.user:
                    player_data["user"] = {
                        "id": player.user.id,
                        "name": player.user.name,
                        "email": player.user.email,
                    }
                response_data["players"].append(player_data)
            
            print("✓ Response data prepared successfully")
            print(f"\nResponse preview: {response_data}")
            
        except Exception as e:
            print(f"✗ Error preparing response: {e}")
            print("Stack trace:")
            traceback.print_exc()
            raise
            
    except Exception as e:
        print(f"\n✗ FATAL ERROR: {e}")
        print("\nFull stack trace:")
        traceback.print_exc()
    finally:
        db.close()

if __name__ == '__main__':
    # Test with game 6 and user 1
    simulate_api_call(game_id=6, user_id=1)