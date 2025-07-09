#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, '/Users/tarikstafford/Desktop/Projects/PadelApp/padel-app/apps/api')

from app.database import get_db
from sqlalchemy import text
import traceback

def test_raw_queries():
    """Test raw SQL queries to identify database issues"""
    db = next(get_db())
    try:
        print("=== Testing Raw Database Queries ===")
        
        # Test 1: Check if game exists
        print("\n1. Checking if game 6 exists:")
        result = db.execute(text("SELECT id, booking_id, club_id, game_status FROM games WHERE id = 6")).fetchone()
        if result:
            print(f"✓ Game found: id={result[0]}, booking_id={result[1]}, club_id={result[2]}, status={result[3]}")
        else:
            print("✗ Game not found!")
            return
        
        booking_id = result[1]
        
        # Test 2: Check booking
        print(f"\n2. Checking booking {booking_id}:")
        result = db.execute(text(f"SELECT id, court_id, user_id FROM bookings WHERE id = {booking_id}")).fetchone()
        if result:
            print(f"✓ Booking found: id={result[0]}, court_id={result[1]}, user_id={result[2]}")
            court_id = result[1]
        else:
            print("✗ Booking not found!")
            return
        
        # Test 3: Check court
        print(f"\n3. Checking court {court_id}:")
        result = db.execute(text(f"SELECT id, name, club_id FROM courts WHERE id = {court_id}")).fetchone()
        if result:
            print(f"✓ Court found: id={result[0]}, name={result[1]}, club_id={result[2]}")
            club_id = result[2]
        else:
            print("✗ Court not found!")
            return
        
        # Test 4: Check club
        print(f"\n4. Checking club {club_id}:")
        result = db.execute(text(f"SELECT id, name FROM clubs WHERE id = {club_id}")).fetchone()
        if result:
            print(f"✓ Club found: id={result[0]}, name={result[1]}")
        else:
            print("✗ Club not found!")
        
        # Test 5: Check game players
        print("\n5. Checking game players:")
        results = db.execute(text("SELECT game_id, user_id, status FROM game_players WHERE game_id = 6")).fetchall()
        print(f"Found {len(results)} players:")
        for r in results:
            print(f"  - User {r[1]}, status: {r[2]}")
            
            # Check if user exists
            user_result = db.execute(text(f"SELECT id, name FROM users WHERE id = {r[1]}")).fetchone()
            if user_result:
                print(f"    ✓ User exists: {user_result[1]}")
            else:
                print(f"    ✗ User {r[1]} NOT FOUND!")
        
        # Test 6: Check for NULL foreign keys
        print("\n6. Checking for NULL foreign keys:")
        
        # Games with null booking_id
        result = db.execute(text("SELECT COUNT(*) FROM games WHERE booking_id IS NULL")).fetchone()
        print(f"Games with NULL booking_id: {result[0]}")
        
        # Bookings with null court_id
        result = db.execute(text("SELECT COUNT(*) FROM bookings WHERE court_id IS NULL")).fetchone()
        print(f"Bookings with NULL court_id: {result[0]}")
        
        # Courts with null club_id
        result = db.execute(text("SELECT COUNT(*) FROM courts WHERE club_id IS NULL")).fetchone()
        print(f"Courts with NULL club_id: {result[0]}")
        
        # Test 7: Test the complex join
        print("\n7. Testing the complex join query:")
        query = """
        SELECT 
            g.id as game_id,
            b.id as booking_id,
            c.id as court_id,
            cl.id as club_id,
            cl.name as club_name
        FROM games g
        LEFT JOIN bookings b ON g.booking_id = b.id
        LEFT JOIN courts c ON b.court_id = c.id
        LEFT JOIN clubs cl ON c.club_id = cl.id
        WHERE g.id = 6
        """
        result = db.execute(text(query)).fetchone()
        if result:
            print("✓ Complex join successful:")
            print(f"  Game: {result[0]}")
            print(f"  Booking: {result[1]}")
            print(f"  Court: {result[2]}")
            print(f"  Club: {result[3]} - {result[4]}")
        else:
            print("✗ Complex join failed!")
            
    except Exception as e:
        print(f"\n✗ Database error: {e}")
        traceback.print_exc()
    finally:
        db.close()

if __name__ == '__main__':
    test_raw_queries()