#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, '/Users/tarikstafford/Desktop/Projects/PadelApp/padel-app/apps/api')

from app.database import get_db
from app.models.game import Game, GameStatus
from datetime import datetime, timezone
import traceback

def test_game_expiration():
    db = next(get_db())
    try:
        print("Testing game expiration logic...")
        
        # Get game
        game = db.query(Game).filter(Game.id == 6).first()
        if not game:
            print("Game not found")
            return
            
        print(f"\nGame details:")
        print(f"ID: {game.id}")
        print(f"Status: {game.game_status}")
        print(f"Start time: {game.start_time}")
        print(f"End time: {game.end_time}")
        
        # Test datetime comparisons
        print(f"\nDatetime tests:")
        current_time = datetime.now(timezone.utc)
        print(f"Current time (UTC): {current_time}")
        
        # Check if end_time has timezone
        print(f"End time type: {type(game.end_time)}")
        print(f"End time tzinfo: {game.end_time.tzinfo}")
        
        # Test is_expired method
        print(f"\nTesting is_expired method:")
        try:
            is_expired = game.is_expired()
            print(f"is_expired() result: {is_expired}")
        except Exception as e:
            print(f"Error in is_expired(): {e}")
            traceback.print_exc()
        
        # Test should_auto_expire method
        print(f"\nTesting should_auto_expire method:")
        try:
            should_expire = game.should_auto_expire()
            print(f"should_auto_expire() result: {should_expire}")
        except Exception as e:
            print(f"Error in should_auto_expire(): {e}")
            traceback.print_exc()
            
        # Test manual comparison
        print(f"\nManual comparison:")
        try:
            # Make end_time timezone aware if it isn't
            if game.end_time.tzinfo is None:
                end_time_aware = game.end_time.replace(tzinfo=timezone.utc)
                print(f"End time made aware: {end_time_aware}")
                manual_expired = current_time > end_time_aware
            else:
                manual_expired = current_time > game.end_time
            print(f"Manual expired check: {manual_expired}")
        except Exception as e:
            print(f"Error in manual comparison: {e}")
            traceback.print_exc()
            
    except Exception as e:
        print(f"Fatal error: {e}")
        traceback.print_exc()
    finally:
        db.close()

if __name__ == '__main__':
    test_game_expiration()