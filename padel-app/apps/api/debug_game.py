#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, '/Users/tarikstafford/Desktop/Projects/PadelApp/padel-app/apps/api')

from app.database import get_db
from app.crud.game_crud import game_crud
from app.services.game_expiration_service import game_expiration_service

def test_game_fetch():
    db = next(get_db())
    try:
        print('Testing game fetch...')
        game = game_crud.get_game(db, 6)
        print(f'Game found: {game}')
        if game:
            print(f'Game booking: {game.booking}')
            print(f'Game players: {game.players}')
            print(f'Game status: {game.game_status}')
            print(f'Should auto expire: {game.should_auto_expire()}')
        else:
            print('Game not found')
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == '__main__':
    test_game_fetch()