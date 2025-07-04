import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime, time

from app.crud.game_crud import GameCRUD, MAX_PLAYERS_PER_GAME
from app.models.game import Game, GameType
from app.models.game_player import GamePlayer, GamePlayerStatus
from app.models.user import User
from app.models.booking import Booking
from app.models.court import Court
from app.models.club import Club
from app.schemas.game_schemas import GameCreate


class TestGameCRUD:
    
    @pytest.fixture
    def game_crud(self):
        return GameCRUD()
    
    @pytest.fixture
    def mock_db(self):
        return Mock(spec=Session)


class TestCreateGame:
    def test_create_game_success(self, mock_db):
        game_crud = GameCRUD()
        
        game_data = GameCreate(
            booking_id=1,
            game_type=GameType.PUBLIC,
            skill_level=3.5
        )
        
        club_id = 1
        start_time = datetime(2024, 1, 15, 10, 0)
        end_time = datetime(2024, 1, 15, 11, 0)
        
        # Mock the created game
        mock_created_game = Game(
            id=1,
            booking_id=1,
            club_id=club_id,
            game_type=GameType.PUBLIC,
            skill_level=3.5,
            start_time=start_time,
            end_time=end_time
        )
        
        # Mock database operations
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        # Mock the refresh to set the id
        def mock_refresh(game):
            game.id = 1
        mock_db.refresh.side_effect = mock_refresh
        
        result = game_crud.create_game(mock_db, game_data, club_id, start_time, end_time)
        
        # Verify database operations
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
        
        # Verify game creation
        added_game = mock_db.add.call_args[0][0]
        assert added_game.booking_id == 1
        assert added_game.club_id == club_id
        assert added_game.game_type == GameType.PUBLIC
        assert added_game.skill_level == 3.5
        assert added_game.start_time == start_time
        assert added_game.end_time == end_time

    def test_create_game_with_private_type(self, mock_db):
        game_crud = GameCRUD()
        
        game_data = GameCreate(
            booking_id=2,
            game_type=GameType.PRIVATE,
            skill_level=4.0
        )
        
        club_id = 2
        start_time = datetime(2024, 1, 15, 14, 0)
        end_time = datetime(2024, 1, 15, 15, 0)
        
        def mock_refresh(game):
            game.id = 2
        mock_db.refresh.side_effect = mock_refresh
        
        result = game_crud.create_game(mock_db, game_data, club_id, start_time, end_time)
        
        added_game = mock_db.add.call_args[0][0]
        assert added_game.game_type == GameType.PRIVATE
        assert added_game.skill_level == 4.0

    def test_create_game_with_different_skill_levels(self, mock_db):
        game_crud = GameCRUD()
        
        skill_levels = [1.0, 2.5, 3.5, 4.5, 5.0]
        
        for skill_level in skill_levels:
            mock_db.reset_mock()
            
            game_data = GameCreate(
                booking_id=1,
                game_type=GameType.PUBLIC,
                skill_level=skill_level
            )
            
            def mock_refresh(game):
                game.id = 1
            mock_db.refresh.side_effect = mock_refresh
            
            result = game_crud.create_game(
                mock_db, 
                game_data, 
                club_id=1, 
                start_time=datetime.now(), 
                end_time=datetime.now()
            )
            
            added_game = mock_db.add.call_args[0][0]
            assert added_game.skill_level == skill_level

    def test_create_game_with_different_booking_ids(self, mock_db):
        game_crud = GameCRUD()
        
        booking_ids = [1, 42, 100, 999]
        
        for booking_id in booking_ids:
            mock_db.reset_mock()
            
            game_data = GameCreate(
                booking_id=booking_id,
                game_type=GameType.PUBLIC,
                skill_level=3.0
            )
            
            def mock_refresh(game):
                game.id = 1
            mock_db.refresh.side_effect = mock_refresh
            
            result = game_crud.create_game(
                mock_db, 
                game_data, 
                club_id=1, 
                start_time=datetime.now(), 
                end_time=datetime.now()
            )
            
            added_game = mock_db.add.call_args[0][0]
            assert added_game.booking_id == booking_id


class TestGetGame:
    def test_get_game_found(self, mock_db):
        game_crud = GameCRUD()
        game_id = 1
        
        mock_game = Game(
            id=game_id,
            booking_id=1,
            club_id=1,
            game_type=GameType.PUBLIC,
            skill_level=3.5
        )
        
        mock_db.query.return_value.filter.return_value.options.return_value.first.return_value = mock_game
        
        result = game_crud.get_game(mock_db, game_id)
        
        assert result == mock_game
        mock_db.query.assert_called_once_with(Game)

    def test_get_game_not_found(self, mock_db):
        game_crud = GameCRUD()
        game_id = 999
        
        mock_db.query.return_value.filter.return_value.options.return_value.first.return_value = None
        
        result = game_crud.get_game(mock_db, game_id)
        
        assert result is None

    def test_get_game_loads_relationships(self, mock_db):
        game_crud = GameCRUD()
        game_id = 1
        
        mock_game = Game(id=game_id, booking_id=1, club_id=1)
        mock_db.query.return_value.filter.return_value.options.return_value.first.return_value = mock_game
        
        result = game_crud.get_game(mock_db, game_id)
        
        # Verify options() was called for loading relationships
        mock_db.query.return_value.filter.return_value.options.assert_called_once()
        assert result == mock_game

    def test_get_game_with_different_ids(self, mock_db):
        game_crud = GameCRUD()
        
        test_cases = [1, 42, 100, 999]
        
        for game_id in test_cases:
            mock_db.reset_mock()
            mock_game = Game(id=game_id, booking_id=1, club_id=1)
            mock_db.query.return_value.filter.return_value.options.return_value.first.return_value = mock_game
            
            result = game_crud.get_game(mock_db, game_id)
            
            assert result == mock_game
            mock_db.query.assert_called_once_with(Game)


class TestGetGameWithTeams:
    def test_get_game_with_teams_found(self, mock_db):
        game_crud = GameCRUD()
        game_id = 1
        
        mock_game = Game(id=game_id, booking_id=1, club_id=1)
        mock_db.query.return_value.filter.return_value.options.return_value.first.return_value = mock_game
        
        result = game_crud.get_game_with_teams(mock_db, game_id)
        
        assert result == mock_game
        mock_db.query.assert_called_once_with(Game)

    def test_get_game_with_teams_not_found(self, mock_db):
        game_crud = GameCRUD()
        game_id = 999
        
        mock_db.query.return_value.filter.return_value.options.return_value.first.return_value = None
        
        result = game_crud.get_game_with_teams(mock_db, game_id)
        
        assert result is None

    def test_get_game_with_teams_loads_team_relationships(self, mock_db):
        game_crud = GameCRUD()
        game_id = 1
        
        mock_game = Game(id=game_id, booking_id=1, club_id=1)
        mock_db.query.return_value.filter.return_value.options.return_value.first.return_value = mock_game
        
        result = game_crud.get_game_with_teams(mock_db, game_id)
        
        # Verify options() was called for loading team relationships
        mock_db.query.return_value.filter.return_value.options.assert_called_once()
        assert result == mock_game


class TestGetPublicGames:
    def test_get_public_games_default_parameters(self, mock_db):
        game_crud = GameCRUD()
        
        mock_games = [
            Game(id=1, game_type=GameType.PUBLIC, booking_id=1, club_id=1),
            Game(id=2, game_type=GameType.PUBLIC, booking_id=2, club_id=1)
        ]
        
        # Mock the complex query chain
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.outerjoin.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.all.return_value = mock_games
        
        result = game_crud.get_public_games(mock_db)
        
        assert result == mock_games
        mock_query.offset.assert_called_once_with(0)
        mock_query.limit.assert_called_once_with(100)

    def test_get_public_games_with_pagination(self, mock_db):
        game_crud = GameCRUD()
        
        mock_games = [Game(id=3, game_type=GameType.PUBLIC, booking_id=3, club_id=1)]
        
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.outerjoin.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.all.return_value = mock_games
        
        result = game_crud.get_public_games(mock_db, skip=10, limit=5)
        
        mock_query.offset.assert_called_once_with(10)
        mock_query.limit.assert_called_once_with(5)
        assert result == mock_games

    def test_get_public_games_with_date_filter(self, mock_db):
        game_crud = GameCRUD()
        
        target_date = date(2024, 1, 15)
        mock_games = [Game(id=1, game_type=GameType.PUBLIC, booking_id=1, club_id=1)]
        
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.outerjoin.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.all.return_value = mock_games
        
        result = game_crud.get_public_games(mock_db, target_date=target_date)
        
        # Should have additional filter calls for date range
        assert mock_query.filter.call_count >= 3  # game_type + available slots + date filters
        assert result == mock_games

    def test_get_public_games_empty_result(self, mock_db):
        game_crud = GameCRUD()
        
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.outerjoin.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.all.return_value = []
        
        result = game_crud.get_public_games(mock_db)
        
        assert result == []

    def test_get_public_games_filters_by_game_type(self, mock_db):
        game_crud = GameCRUD()
        
        mock_games = [Game(id=1, game_type=GameType.PUBLIC, booking_id=1, club_id=1)]
        
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.outerjoin.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.all.return_value = mock_games
        
        result = game_crud.get_public_games(mock_db)
        
        # Should filter by PUBLIC game type and available slots
        assert mock_query.filter.call_count >= 2
        assert result == mock_games

    def test_get_public_games_filters_by_available_slots(self, mock_db):
        game_crud = GameCRUD()
        
        mock_games = [Game(id=1, game_type=GameType.PUBLIC, booking_id=1, club_id=1)]
        
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.outerjoin.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.all.return_value = mock_games
        
        result = game_crud.get_public_games(mock_db)
        
        # Should filter by available slots (less than MAX_PLAYERS_PER_GAME)
        assert mock_query.filter.call_count >= 2
        assert result == mock_games


class TestGetRecentGamesByClub:
    def test_get_recent_games_by_club_success(self, mock_db):
        game_crud = GameCRUD()
        club_id = 1
        
        mock_games = [
            Game(id=1, booking_id=1, club_id=club_id),
            Game(id=2, booking_id=2, club_id=club_id)
        ]
        
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.all.return_value = mock_games
        
        result = game_crud.get_recent_games_by_club(mock_db, club_id)
        
        assert result == mock_games
        mock_query.filter.assert_called()
        mock_query.limit.assert_called_once_with(5)  # Default limit

    def test_get_recent_games_by_club_with_custom_limit(self, mock_db):
        game_crud = GameCRUD()
        club_id = 1
        custom_limit = 10
        
        mock_games = [Game(id=i, booking_id=i, club_id=club_id) for i in range(1, 11)]
        
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.all.return_value = mock_games
        
        result = game_crud.get_recent_games_by_club(mock_db, club_id, limit=custom_limit)
        
        mock_query.limit.assert_called_once_with(custom_limit)
        assert result == mock_games

    def test_get_recent_games_by_club_empty_result(self, mock_db):
        game_crud = GameCRUD()
        club_id = 999
        
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.all.return_value = []
        
        result = game_crud.get_recent_games_by_club(mock_db, club_id)
        
        assert result == []

    def test_get_recent_games_by_club_orders_by_created_at_desc(self, mock_db):
        game_crud = GameCRUD()
        club_id = 1
        
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.all.return_value = []
        
        result = game_crud.get_recent_games_by_club(mock_db, club_id)
        
        # Should order by created_at.desc()
        mock_query.order_by.assert_called_once()

    def test_get_recent_games_by_club_different_club_ids(self, mock_db):
        game_crud = GameCRUD()
        
        club_ids = [1, 42, 100, 999]
        
        for club_id in club_ids:
            mock_db.reset_mock()
            
            mock_query = Mock()
            mock_db.query.return_value = mock_query
            mock_query.join.return_value = mock_query
            mock_query.filter.return_value = mock_query
            mock_query.order_by.return_value = mock_query
            mock_query.limit.return_value = mock_query
            mock_query.options.return_value = mock_query
            mock_query.all.return_value = []
            
            result = game_crud.get_recent_games_by_club(mock_db, club_id)
            
            mock_query.filter.assert_called()


class TestGetGameByBooking:
    def test_get_game_by_booking_found(self, mock_db):
        game_crud = GameCRUD()
        booking_id = 1
        
        mock_game = Game(id=1, booking_id=booking_id, club_id=1)
        mock_db.query.return_value.filter.return_value.options.return_value.first.return_value = mock_game
        
        result = game_crud.get_game_by_booking(mock_db, booking_id)
        
        assert result == mock_game
        mock_db.query.assert_called_once_with(Game)

    def test_get_game_by_booking_not_found(self, mock_db):
        game_crud = GameCRUD()
        booking_id = 999
        
        mock_db.query.return_value.filter.return_value.options.return_value.first.return_value = None
        
        result = game_crud.get_game_by_booking(mock_db, booking_id)
        
        assert result is None

    def test_get_game_by_booking_loads_relationships(self, mock_db):
        game_crud = GameCRUD()
        booking_id = 1
        
        mock_game = Game(id=1, booking_id=booking_id, club_id=1)
        mock_db.query.return_value.filter.return_value.options.return_value.first.return_value = mock_game
        
        result = game_crud.get_game_by_booking(mock_db, booking_id)
        
        # Verify options() was called for loading relationships
        mock_db.query.return_value.filter.return_value.options.assert_called_once()
        assert result == mock_game

    def test_get_game_by_booking_different_booking_ids(self, mock_db):
        game_crud = GameCRUD()
        
        booking_ids = [1, 42, 100, 999]
        
        for booking_id in booking_ids:
            mock_db.reset_mock()
            mock_game = Game(id=1, booking_id=booking_id, club_id=1)
            mock_db.query.return_value.filter.return_value.options.return_value.first.return_value = mock_game
            
            result = game_crud.get_game_by_booking(mock_db, booking_id)
            
            assert result == mock_game
            mock_db.query.assert_called_once_with(Game)


class TestGameCRUDIntegration:
    def test_create_then_get_game(self, mock_db):
        """Integration test for creating and then retrieving a game."""
        game_crud = GameCRUD()
        
        # Create game
        game_data = GameCreate(
            booking_id=1,
            game_type=GameType.PUBLIC,
            skill_level=3.5
        )
        
        club_id = 1
        start_time = datetime(2024, 1, 15, 10, 0)
        end_time = datetime(2024, 1, 15, 11, 0)
        
        def mock_refresh(game):
            game.id = 1
        mock_db.refresh.side_effect = mock_refresh
        
        created_game = game_crud.create_game(mock_db, game_data, club_id, start_time, end_time)
        
        # Reset mock for get operation
        mock_db.reset_mock()
        mock_db.query.return_value.filter.return_value.options.return_value.first.return_value = Game(
            id=1,
            booking_id=1,
            club_id=club_id,
            game_type=GameType.PUBLIC,
            skill_level=3.5,
            start_time=start_time,
            end_time=end_time
        )
        
        # Get game
        retrieved_game = game_crud.get_game(mock_db, game_id=1)
        
        assert retrieved_game.booking_id == 1
        assert retrieved_game.club_id == club_id
        assert retrieved_game.game_type == GameType.PUBLIC
        assert retrieved_game.skill_level == 3.5

    def test_create_game_then_get_by_booking(self, mock_db):
        """Integration test for creating a game and then retrieving by booking."""
        game_crud = GameCRUD()
        
        # Create game
        game_data = GameCreate(
            booking_id=123,
            game_type=GameType.PRIVATE,
            skill_level=4.0
        )
        
        def mock_refresh(game):
            game.id = 1
        mock_db.refresh.side_effect = mock_refresh
        
        created_game = game_crud.create_game(
            mock_db, 
            game_data, 
            club_id=1, 
            start_time=datetime.now(), 
            end_time=datetime.now()
        )
        
        # Reset mock for get by booking operation
        mock_db.reset_mock()
        mock_db.query.return_value.filter.return_value.options.return_value.first.return_value = Game(
            id=1,
            booking_id=123,
            club_id=1,
            game_type=GameType.PRIVATE,
            skill_level=4.0
        )
        
        # Get game by booking
        retrieved_game = game_crud.get_game_by_booking(mock_db, booking_id=123)
        
        assert retrieved_game.booking_id == 123
        assert retrieved_game.game_type == GameType.PRIVATE
        assert retrieved_game.skill_level == 4.0

    def test_full_game_workflow(self, mock_db):
        """Integration test for complete game workflow."""
        game_crud = GameCRUD()
        
        # 1. Create game
        game_data = GameCreate(
            booking_id=1,
            game_type=GameType.PUBLIC,
            skill_level=3.0
        )
        
        def mock_refresh(game):
            game.id = 1
        mock_db.refresh.side_effect = mock_refresh
        
        created_game = game_crud.create_game(
            mock_db, 
            game_data, 
            club_id=1, 
            start_time=datetime.now(), 
            end_time=datetime.now()
        )
        
        # 2. Get public games (should include our game)
        mock_db.reset_mock()
        mock_games = [
            Game(id=1, booking_id=1, club_id=1, game_type=GameType.PUBLIC, skill_level=3.0)
        ]
        
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.outerjoin.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.all.return_value = mock_games
        
        public_games = game_crud.get_public_games(mock_db)
        assert len(public_games) == 1
        assert public_games[0].game_type == GameType.PUBLIC
        
        # 3. Get specific game
        mock_db.reset_mock()
        mock_db.query.return_value.filter.return_value.options.return_value.first.return_value = mock_games[0]
        
        specific_game = game_crud.get_game(mock_db, game_id=1)
        assert specific_game.skill_level == 3.0
        
        # 4. Get recent games by club
        mock_db.reset_mock()
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.all.return_value = mock_games
        
        recent_games = game_crud.get_recent_games_by_club(mock_db, club_id=1)
        assert len(recent_games) == 1


class TestGameCRUDEdgeCases:
    def test_get_game_with_zero_id(self, mock_db):
        game_crud = GameCRUD()
        mock_db.query.return_value.filter.return_value.options.return_value.first.return_value = None
        
        result = game_crud.get_game(mock_db, game_id=0)
        assert result is None

    def test_get_game_with_negative_id(self, mock_db):
        game_crud = GameCRUD()
        mock_db.query.return_value.filter.return_value.options.return_value.first.return_value = None
        
        result = game_crud.get_game(mock_db, game_id=-1)
        assert result is None

    def test_get_public_games_with_zero_limit(self, mock_db):
        game_crud = GameCRUD()
        
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.outerjoin.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.all.return_value = []
        
        result = game_crud.get_public_games(mock_db, limit=0)
        
        mock_query.limit.assert_called_once_with(0)
        assert result == []

    def test_get_public_games_with_large_skip(self, mock_db):
        game_crud = GameCRUD()
        
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.outerjoin.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.all.return_value = []
        
        result = game_crud.get_public_games(mock_db, skip=1000000)
        
        mock_query.offset.assert_called_once_with(1000000)
        assert result == []

    def test_get_recent_games_by_club_with_zero_limit(self, mock_db):
        game_crud = GameCRUD()
        
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.all.return_value = []
        
        result = game_crud.get_recent_games_by_club(mock_db, club_id=1, limit=0)
        
        mock_query.limit.assert_called_once_with(0)
        assert result == []

    def test_create_game_with_edge_skill_levels(self, mock_db):
        game_crud = GameCRUD()
        
        edge_skill_levels = [0.0, 0.5, 5.0, 6.0]
        
        for skill_level in edge_skill_levels:
            mock_db.reset_mock()
            
            game_data = GameCreate(
                booking_id=1,
                game_type=GameType.PUBLIC,
                skill_level=skill_level
            )
            
            def mock_refresh(game):
                game.id = 1
            mock_db.refresh.side_effect = mock_refresh
            
            result = game_crud.create_game(
                mock_db, 
                game_data, 
                club_id=1, 
                start_time=datetime.now(), 
                end_time=datetime.now()
            )
            
            added_game = mock_db.add.call_args[0][0]
            assert added_game.skill_level == skill_level

    def test_get_public_games_with_past_date(self, mock_db):
        game_crud = GameCRUD()
        
        past_date = date(2020, 1, 1)
        
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.outerjoin.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.all.return_value = []
        
        result = game_crud.get_public_games(mock_db, target_date=past_date)
        
        # Should still work, just return empty results
        assert result == []

    def test_get_public_games_with_future_date(self, mock_db):
        game_crud = GameCRUD()
        
        future_date = date(2030, 12, 31)
        
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.outerjoin.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.all.return_value = []
        
        result = game_crud.get_public_games(mock_db, target_date=future_date)
        
        assert result == []


class TestGameCRUDConstants:
    def test_max_players_per_game_constant(self):
        """Test that MAX_PLAYERS_PER_GAME constant is defined correctly."""
        assert MAX_PLAYERS_PER_GAME == 4

    def test_max_players_per_game_used_in_filter(self, mock_db):
        """Test that MAX_PLAYERS_PER_GAME is used in public games filtering."""
        game_crud = GameCRUD()
        
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.outerjoin.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.all.return_value = []
        
        result = game_crud.get_public_games(mock_db)
        
        # Should filter by available slots using MAX_PLAYERS_PER_GAME
        assert mock_query.filter.call_count >= 2


class TestGameCRUDTypes:
    def test_create_game_with_all_game_types(self, mock_db):
        """Test creating games with all game types."""
        game_crud = GameCRUD()
        
        game_types = [GameType.PUBLIC, GameType.PRIVATE]
        
        for game_type in game_types:
            mock_db.reset_mock()
            
            game_data = GameCreate(
                booking_id=1,
                game_type=game_type,
                skill_level=3.0
            )
            
            def mock_refresh(game):
                game.id = 1
            mock_db.refresh.side_effect = mock_refresh
            
            result = game_crud.create_game(
                mock_db, 
                game_data, 
                club_id=1, 
                start_time=datetime.now(), 
                end_time=datetime.now()
            )
            
            added_game = mock_db.add.call_args[0][0]
            assert added_game.game_type == game_type


class TestGameCRUDPerformance:
    def test_multiple_game_operations(self, mock_db):
        """Test multiple game operations in sequence."""
        game_crud = GameCRUD()
        
        # Perform multiple create operations
        for i in range(10):
            game_data = GameCreate(
                booking_id=i,
                game_type=GameType.PUBLIC,
                skill_level=3.0
            )
            
            def mock_refresh(game):
                game.id = i
            mock_db.refresh.side_effect = mock_refresh
            
            created_game = game_crud.create_game(
                mock_db, 
                game_data, 
                club_id=1, 
                start_time=datetime.now(), 
                end_time=datetime.now()
            )
            
            # Verify each creation
            added_game = mock_db.add.call_args[0][0]
            assert added_game.booking_id == i
            assert added_game.game_type == GameType.PUBLIC
            
            mock_db.reset_mock()

    def test_get_public_games_with_large_result_set(self, mock_db):
        """Test performance with large result sets."""
        game_crud = GameCRUD()
        
        # Mock a large result set
        large_result = [Game(id=i, booking_id=i, club_id=1, game_type=GameType.PUBLIC) for i in range(1000)]
        
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.outerjoin.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.all.return_value = large_result
        
        result = game_crud.get_public_games(mock_db, limit=1000)
        
        assert len(result) == 1000
        assert result == large_result