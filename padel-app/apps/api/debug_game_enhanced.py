#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, '/Users/tarikstafford/Desktop/Projects/PadelApp/padel-app/apps/api')

from app.database import get_db
from app.crud.game_crud import game_crud
from app.services.game_expiration_service import game_expiration_service
from app.models.game import Game, GameStatus
from sqlalchemy.orm import Session
import traceback

def debug_game_expiration(db: Session, game_id: int):
    """Test the game expiration service"""
    print(f"\n=== Testing Game Expiration Service for Game ID {game_id} ===")
    try:
        # First get the game directly
        game = db.query(Game).filter(Game.id == game_id).first()
        if game:
            print(f"Game status: {game.game_status}")
            print(f"Start time: {game.start_time}")
            print(f"End time: {game.end_time}")
            print(f"Is expired: {game.is_expired()}")
            print(f"Should auto expire: {game.should_auto_expire()}")
        
        # Now test the expiration service
        print("\nTesting expiration service...")
        result = game_expiration_service.check_single_game_expiration(db, game_id)
        print(f"Expiration check result: {result}")
    except Exception as e:
        print(f"Error in expiration service: {e}")
        traceback.print_exc()

def debug_game_relationships(db: Session, game_id: int):
    """Test game relationships loading"""
    print(f"\n=== Testing Game Relationships for Game ID {game_id} ===")
    try:
        # Test basic query
        print("1. Testing basic game query...")
        game = db.query(Game).filter(Game.id == game_id).first()
        if not game:
            print("Game not found!")
            return
        print(f"Game found: ID={game.id}, booking_id={game.booking_id}")
        
        # Test booking relationship
        print("\n2. Testing booking relationship...")
        if game.booking_id:
            booking = game.booking
            if booking:
                print(f"Booking found: ID={booking.id}")
                
                # Test court relationship
                print("\n3. Testing court relationship...")
                if booking.court:
                    print(f"Court found: ID={booking.court.id}, name={booking.court.name}")
                    
                    # Test club relationship
                    print("\n4. Testing club relationship...")
                    if booking.court.club:
                        print(f"Club found: ID={booking.court.club.id}, name={booking.court.club.name}")
                    else:
                        print("ERROR: Club not found for court!")
                else:
                    print("ERROR: Court not found for booking!")
            else:
                print("ERROR: Booking not found!")
        
        # Test players relationship
        print("\n5. Testing players relationship...")
        if game.players:
            print(f"Found {len(game.players)} players")
            for player in game.players:
                if player.user:
                    print(f"  - Player: {player.user.name} (ID={player.user_id}, status={player.status})")
                else:
                    print(f"  - ERROR: User not found for player with user_id={player.user_id}")
        else:
            print("No players found")
            
    except Exception as e:
        print(f"Error testing relationships: {e}")
        traceback.print_exc()

def test_game_crud_method(db: Session, game_id: int):
    """Test the game_crud.get_game method with eager loading"""
    print(f"\n=== Testing game_crud.get_game for Game ID {game_id} ===")
    try:
        game = game_crud.get_game(db, game_id)
        if not game:
            print("Game not found via game_crud!")
            return
            
        print(f"Game found: ID={game.id}")
        
        # Check if relationships are loaded
        print("\nChecking eager-loaded relationships:")
        
        # Check booking
        try:
            if game.booking:
                print(f"✓ Booking loaded: ID={game.booking.id}")
                
                # Check court
                try:
                    if game.booking.court:
                        print(f"✓ Court loaded: ID={game.booking.court.id}")
                        
                        # Check club
                        try:
                            if game.booking.court.club:
                                print(f"✓ Club loaded: ID={game.booking.court.club.id}")
                            else:
                                print("✗ Club is None")
                        except Exception as e:
                            print(f"✗ Error accessing club: {e}")
                    else:
                        print("✗ Court is None")
                except Exception as e:
                    print(f"✗ Error accessing court: {e}")
            else:
                print("✗ Booking is None")
        except Exception as e:
            print(f"✗ Error accessing booking: {e}")
        
        # Check players
        try:
            if game.players:
                print(f"✓ Players loaded: {len(game.players)} players")
                for i, player in enumerate(game.players):
                    try:
                        if player.user:
                            print(f"  ✓ Player {i+1}: {player.user.name}")
                        else:
                            print(f"  ✗ Player {i+1}: User is None (user_id={player.user_id})")
                    except Exception as e:
                        print(f"  ✗ Player {i+1}: Error accessing user - {e}")
            else:
                print("✗ No players found")
        except Exception as e:
            print(f"✗ Error accessing players: {e}")
            
    except Exception as e:
        print(f"Error in game_crud.get_game: {e}")
        traceback.print_exc()

def check_database_integrity(db: Session, game_id: int):
    """Check database integrity for the game"""
    print(f"\n=== Checking Database Integrity for Game ID {game_id} ===")
    
    # Check game exists
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        print(f"ERROR: Game with ID {game_id} not found!")
        return
        
    print(f"Game found: booking_id={game.booking_id}, club_id={game.club_id}")
    
    # Check booking exists
    if game.booking_id:
        from app.models.booking import Booking
        booking = db.query(Booking).filter(Booking.id == game.booking_id).first()
        if booking:
            print(f"✓ Booking exists: court_id={booking.court_id}")
            
            # Check court exists
            if booking.court_id:
                from app.models.court import Court
                court = db.query(Court).filter(Court.id == booking.court_id).first()
                if court:
                    print(f"✓ Court exists: club_id={court.club_id}")
                    
                    # Check club exists
                    if court.club_id:
                        from app.models.club import Club
                        club = db.query(Club).filter(Club.id == court.club_id).first()
                        if club:
                            print(f"✓ Club exists: name={club.name}")
                        else:
                            print(f"✗ ERROR: Club with ID {court.club_id} not found!")
                    else:
                        print("✗ ERROR: Court has no club_id!")
                else:
                    print(f"✗ ERROR: Court with ID {booking.court_id} not found!")
            else:
                print("✗ ERROR: Booking has no court_id!")
        else:
            print(f"✗ ERROR: Booking with ID {game.booking_id} not found!")
    else:
        print("✗ ERROR: Game has no booking_id!")
    
    # Check players
    from app.models.game_player import GamePlayer
    players = db.query(GamePlayer).filter(GamePlayer.game_id == game_id).all()
    print(f"\nFound {len(players)} players for this game")
    
    for player in players:
        from app.models.user import User
        user = db.query(User).filter(User.id == player.user_id).first()
        if user:
            print(f"✓ Player user exists: {user.name} (ID={user.id})")
        else:
            print(f"✗ ERROR: User with ID {player.user_id} not found!")

def main():
    db = next(get_db())
    game_id = 6
    
    try:
        print(f"========== DEBUGGING GAME {game_id} ==========")
        
        # Check database integrity first
        check_database_integrity(db, game_id)
        
        # Test basic relationships
        debug_game_relationships(db, game_id)
        
        # Test game_crud method
        test_game_crud_method(db, game_id)
        
        # Test expiration service
        debug_game_expiration(db, game_id)
        
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        traceback.print_exc()
    finally:
        db.close()

if __name__ == '__main__':
    main()