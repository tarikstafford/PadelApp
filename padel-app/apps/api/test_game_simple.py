#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, '/Users/tarikstafford/Desktop/Projects/PadelApp/padel-app/apps/api')

from app.database import get_db
from app.models.game import Game
from sqlalchemy.orm import joinedload

def test_simple_game_query():
    db = next(get_db())
    try:
        print("Testing simple game query...")
        
        # Test 1: Basic game query
        print("\n1. Basic query:")
        game = db.query(Game).filter(Game.id == 6).first()
        if game:
            print(f"Game found: ID={game.id}, booking_id={game.booking_id}")
        else:
            print("Game not found")
            return
        
        # Test 2: Access booking without eager loading
        print("\n2. Accessing booking (lazy load):")
        try:
            booking = game.booking
            if booking:
                print(f"Booking found: ID={booking.id}")
            else:
                print("Booking is None")
        except Exception as e:
            print(f"Error accessing booking: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 3: Query with eager loading
        print("\n3. Query with eager loading:")
        try:
            game_eager = (
                db.query(Game)
                .filter(Game.id == 6)
                .options(joinedload(Game.booking))
                .first()
            )
            if game_eager and game_eager.booking:
                print(f"Game with booking loaded: booking ID={game_eager.booking.id}")
            else:
                print("Failed to load with eager loading")
        except Exception as e:
            print(f"Error with eager loading: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == '__main__':
    test_simple_game_query()