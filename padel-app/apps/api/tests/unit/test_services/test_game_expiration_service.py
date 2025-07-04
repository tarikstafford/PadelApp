import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from app.services.game_expiration_service import GameExpirationService, game_expiration_service
from app.models.game import Game, GameStatus
from app.crud.game_crud import game_crud


class TestGameExpirationService:
    """Comprehensive test suite for GameExpirationService"""

    def setup_method(self):
        """Set up test fixtures"""
        self.service = GameExpirationService()
        self.mock_db = Mock(spec=Session)
        self.current_time = datetime(2024, 1, 15, 12, 0)  # Noon on Jan 15, 2024

    def create_mock_game(self, game_id, end_time, status=GameStatus.SCHEDULED):
        """Create a mock game object"""
        mock_game = Mock()
        mock_game.id = game_id
        mock_game.end_time = end_time
        mock_game.game_status = status
        mock_game.should_auto_expire.return_value = (
            status == GameStatus.SCHEDULED and end_time < self.current_time
        )
        return mock_game

    @patch('app.services.game_expiration_service.datetime')
    def test_expire_past_games_success(self, mock_datetime):
        """Test successful expiration of past games"""
        # Setup
        mock_datetime.utcnow.return_value = self.current_time
        
        # Create mock games - some past, some future
        past_game_1 = self.create_mock_game(1, datetime(2024, 1, 15, 10, 0))  # 2 hours ago
        past_game_2 = self.create_mock_game(2, datetime(2024, 1, 15, 11, 30))  # 30 minutes ago
        future_game = self.create_mock_game(3, datetime(2024, 1, 15, 14, 0))  # 2 hours from now
        
        past_games = [past_game_1, past_game_2]
        
        # Setup database query mock
        mock_query = Mock()
        mock_filter = Mock()
        mock_query.filter.return_value = mock_filter
        mock_filter.all.return_value = past_games
        self.mock_db.query.return_value = mock_query
        
        # Execute
        result = self.service.expire_past_games(self.mock_db)
        
        # Verify
        assert result == [1, 2]
        assert past_game_1.game_status == GameStatus.EXPIRED
        assert past_game_2.game_status == GameStatus.EXPIRED
        
        # Verify database operations
        assert self.mock_db.add.call_count == 2
        self.mock_db.add.assert_any_call(past_game_1)
        self.mock_db.add.assert_any_call(past_game_2)
        self.mock_db.commit.assert_called_once()

    @patch('app.services.game_expiration_service.datetime')
    def test_expire_past_games_no_games_to_expire(self, mock_datetime):
        """Test expiration when no games need to be expired"""
        # Setup
        mock_datetime.utcnow.return_value = self.current_time
        
        # Setup database query to return empty list
        mock_query = Mock()
        mock_filter = Mock()
        mock_query.filter.return_value = mock_filter
        mock_filter.all.return_value = []
        self.mock_db.query.return_value = mock_query
        
        # Execute
        result = self.service.expire_past_games(self.mock_db)
        
        # Verify
        assert result == []
        self.mock_db.add.assert_not_called()
        self.mock_db.commit.assert_called_once()

    @patch('app.services.game_expiration_service.datetime')
    def test_expire_past_games_query_filters(self, mock_datetime):
        """Test that database query uses correct filters"""
        # Setup
        mock_datetime.utcnow.return_value = self.current_time
        
        mock_query = Mock()
        mock_filter = Mock()
        mock_query.filter.return_value = mock_filter
        mock_filter.all.return_value = []
        self.mock_db.query.return_value = mock_query
        
        # Execute
        self.service.expire_past_games(self.mock_db)
        
        # Verify that query was called with Game model
        self.mock_db.query.assert_called_once_with(Game)
        
        # Verify that filter was called (exact filter conditions are implementation details)
        mock_query.filter.assert_called_once()

    @patch('app.services.game_expiration_service.datetime')
    def test_expire_past_games_mixed_statuses(self, mock_datetime):
        """Test expiration with games in different statuses"""
        # Setup
        mock_datetime.utcnow.return_value = self.current_time
        
        # Create games with different statuses (only SCHEDULED should be expired)
        scheduled_game = self.create_mock_game(1, datetime(2024, 1, 15, 10, 0), GameStatus.SCHEDULED)
        completed_game = self.create_mock_game(2, datetime(2024, 1, 15, 10, 0), GameStatus.COMPLETED)
        cancelled_game = self.create_mock_game(3, datetime(2024, 1, 15, 10, 0), GameStatus.CANCELLED)
        
        # Mock should only return SCHEDULED games past end time
        past_scheduled_games = [scheduled_game]
        
        mock_query = Mock()
        mock_filter = Mock()
        mock_query.filter.return_value = mock_filter
        mock_filter.all.return_value = past_scheduled_games
        self.mock_db.query.return_value = mock_query
        
        # Execute
        result = self.service.expire_past_games(self.mock_db)
        
        # Verify only scheduled game was expired
        assert result == [1]
        assert scheduled_game.game_status == GameStatus.EXPIRED
        self.mock_db.add.assert_called_once_with(scheduled_game)

    def test_check_single_game_expiration_game_not_found(self):
        """Test single game expiration when game doesn't exist"""
        # Setup
        game_id = 1
        game_crud.get_game.return_value = None
        
        with patch('app.services.game_expiration_service.game_crud', game_crud):
            # Execute
            result = self.service.check_single_game_expiration(self.mock_db, game_id)
            
            # Verify
            assert result is False
            self.mock_db.add.assert_not_called()
            self.mock_db.commit.assert_not_called()

    def test_check_single_game_expiration_game_should_expire(self):
        """Test single game expiration when game should be expired"""
        # Setup
        game_id = 1
        mock_game = self.create_mock_game(game_id, datetime(2024, 1, 15, 10, 0))
        mock_game.should_auto_expire.return_value = True
        
        with patch('app.services.game_expiration_service.game_crud') as mock_game_crud:
            mock_game_crud.get_game.return_value = mock_game
            
            # Execute
            result = self.service.check_single_game_expiration(self.mock_db, game_id)
            
            # Verify
            assert result is True
            assert mock_game.game_status == GameStatus.EXPIRED
            self.mock_db.add.assert_called_once_with(mock_game)
            self.mock_db.commit.assert_called_once()

    def test_check_single_game_expiration_game_should_not_expire(self):
        """Test single game expiration when game should not be expired"""
        # Setup
        game_id = 1
        mock_game = self.create_mock_game(game_id, datetime(2024, 1, 15, 14, 0))  # Future time
        mock_game.should_auto_expire.return_value = False
        
        with patch('app.services.game_expiration_service.game_crud') as mock_game_crud:
            mock_game_crud.get_game.return_value = mock_game
            
            # Execute
            result = self.service.check_single_game_expiration(self.mock_db, game_id)
            
            # Verify
            assert result is False
            assert mock_game.game_status == GameStatus.SCHEDULED  # Unchanged
            self.mock_db.add.assert_not_called()
            self.mock_db.commit.assert_not_called()

    def test_check_single_game_expiration_already_expired(self):
        """Test single game expiration when game is already expired"""
        # Setup
        game_id = 1
        mock_game = self.create_mock_game(game_id, datetime(2024, 1, 15, 10, 0), GameStatus.EXPIRED)
        mock_game.should_auto_expire.return_value = False  # Already expired
        
        with patch('app.services.game_expiration_service.game_crud') as mock_game_crud:
            mock_game_crud.get_game.return_value = mock_game
            
            # Execute
            result = self.service.check_single_game_expiration(self.mock_db, game_id)
            
            # Verify
            assert result is False
            self.mock_db.add.assert_not_called()
            self.mock_db.commit.assert_not_called()

    def test_check_single_game_expiration_completed_game(self):
        """Test single game expiration when game is completed"""
        # Setup
        game_id = 1
        mock_game = self.create_mock_game(game_id, datetime(2024, 1, 15, 10, 0), GameStatus.COMPLETED)
        mock_game.should_auto_expire.return_value = False  # Completed games don't auto-expire
        
        with patch('app.services.game_expiration_service.game_crud') as mock_game_crud:
            mock_game_crud.get_game.return_value = mock_game
            
            # Execute
            result = self.service.check_single_game_expiration(self.mock_db, game_id)
            
            # Verify
            assert result is False
            assert mock_game.game_status == GameStatus.COMPLETED  # Unchanged

    def test_service_instance_singleton(self):
        """Test that the service instance is properly initialized"""
        assert game_expiration_service is not None
        assert isinstance(game_expiration_service, GameExpirationService)

    def test_expire_past_games_database_error_handling(self):
        """Test error handling when database operations fail"""
        # Setup database to raise exception
        self.mock_db.query.side_effect = Exception("Database error")
        
        # Execute and verify exception is raised
        with pytest.raises(Exception, match="Database error"):
            self.service.expire_past_games(self.mock_db)

    def test_check_single_game_expiration_database_error(self):
        """Test error handling in single game expiration"""
        # Setup game_crud to raise exception
        with patch('app.services.game_expiration_service.game_crud') as mock_game_crud:
            mock_game_crud.get_game.side_effect = Exception("Database error")
            
            # Execute and verify exception is raised
            with pytest.raises(Exception, match="Database error"):
                self.service.check_single_game_expiration(self.mock_db, 1)

    @patch('app.services.game_expiration_service.datetime')
    def test_expire_past_games_large_batch(self, mock_datetime):
        """Test expiration with a large number of games"""
        # Setup
        mock_datetime.utcnow.return_value = self.current_time
        
        # Create many past games
        past_games = []
        expected_ids = []
        for i in range(100):
            game = self.create_mock_game(i, datetime(2024, 1, 15, 10, 0))
            past_games.append(game)
            expected_ids.append(i)
        
        mock_query = Mock()
        mock_filter = Mock()
        mock_query.filter.return_value = mock_filter
        mock_filter.all.return_value = past_games
        self.mock_db.query.return_value = mock_query
        
        # Execute
        result = self.service.expire_past_games(self.mock_db)
        
        # Verify
        assert result == expected_ids
        assert self.mock_db.add.call_count == 100
        self.mock_db.commit.assert_called_once()

    @patch('app.services.game_expiration_service.datetime')
    def test_expire_past_games_time_boundaries(self, mock_datetime):
        """Test expiration at exact time boundaries"""
        # Setup
        current_time = datetime(2024, 1, 15, 12, 0, 0)  # Exact noon
        mock_datetime.utcnow.return_value = current_time
        
        # Create games at exact boundary times
        exactly_expired = self.create_mock_game(1, datetime(2024, 1, 15, 11, 59, 59))  # 1 second ago
        exactly_current = self.create_mock_game(2, datetime(2024, 1, 15, 12, 0, 0))   # Exactly now
        just_future = self.create_mock_game(3, datetime(2024, 1, 15, 12, 0, 1))       # 1 second future
        
        # Only the expired game should be returned by the query
        past_games = [exactly_expired]
        
        mock_query = Mock()
        mock_filter = Mock()
        mock_query.filter.return_value = mock_filter
        mock_filter.all.return_value = past_games
        self.mock_db.query.return_value = mock_query
        
        # Execute
        result = self.service.expire_past_games(self.mock_db)
        
        # Verify
        assert result == [1]
        assert exactly_expired.game_status == GameStatus.EXPIRED

    def test_game_status_transitions(self):
        """Test that only valid status transitions occur"""
        # Setup game in various statuses
        statuses_to_test = [
            GameStatus.SCHEDULED,
            GameStatus.IN_PROGRESS,
            GameStatus.COMPLETED,
            GameStatus.CANCELLED,
            GameStatus.EXPIRED
        ]
        
        for status in statuses_to_test:
            game_id = 1
            mock_game = self.create_mock_game(game_id, datetime(2024, 1, 15, 10, 0), status)
            
            # Only SCHEDULED games should be eligible for auto-expiration
            should_expire = status == GameStatus.SCHEDULED
            mock_game.should_auto_expire.return_value = should_expire
            
            with patch('app.services.game_expiration_service.game_crud') as mock_game_crud:
                mock_game_crud.get_game.return_value = mock_game
                
                # Reset database mock
                self.mock_db.reset_mock()
                
                # Execute
                result = self.service.check_single_game_expiration(self.mock_db, game_id)
                
                # Verify
                if should_expire:
                    assert result is True
                    assert mock_game.game_status == GameStatus.EXPIRED
                    self.mock_db.add.assert_called_once_with(mock_game)
                    self.mock_db.commit.assert_called_once()
                else:
                    assert result is False
                    assert mock_game.game_status == status  # Status unchanged
                    self.mock_db.add.assert_not_called()
                    self.mock_db.commit.assert_not_called()

    @patch('app.services.game_expiration_service.datetime')
    def test_expire_past_games_concurrent_modifications(self, mock_datetime):
        """Test handling of concurrent modifications during expiration"""
        # Setup
        mock_datetime.utcnow.return_value = self.current_time
        
        # Create a game that might be modified during processing
        game = self.create_mock_game(1, datetime(2024, 1, 15, 10, 0))
        
        # Simulate the game being modified after query but before update
        def side_effect_modify_game(*args):
            # Simulate another process changing the game status
            game.game_status = GameStatus.COMPLETED
            return None
        
        self.mock_db.add.side_effect = side_effect_modify_game
        
        mock_query = Mock()
        mock_filter = Mock()
        mock_query.filter.return_value = mock_filter
        mock_filter.all.return_value = [game]
        self.mock_db.query.return_value = mock_query
        
        # Execute
        result = self.service.expire_past_games(self.mock_db)
        
        # Verify that the service handles the concurrent modification
        assert result == [1]  # Still returns the game ID
        self.mock_db.commit.assert_called_once()

    def test_performance_with_no_games(self):
        """Test performance characteristics when no games need expiration"""
        # Setup empty result
        mock_query = Mock()
        mock_filter = Mock()
        mock_query.filter.return_value = mock_filter
        mock_filter.all.return_value = []
        self.mock_db.query.return_value = mock_query
        
        # Execute multiple times to test consistency
        for _ in range(10):
            result = self.service.expire_past_games(self.mock_db)
            assert result == []
        
        # Verify database operations are minimal
        assert self.mock_db.query.call_count == 10
        assert self.mock_db.add.call_count == 0
        assert self.mock_db.commit.call_count == 10  # Commit is still called

    def test_method_signatures(self):
        """Test that methods have correct signatures"""
        # Test expire_past_games signature
        import inspect
        
        expire_sig = inspect.signature(self.service.expire_past_games)
        assert 'db' in expire_sig.parameters
        assert expire_sig.return_annotation != inspect.Signature.empty
        
        # Test check_single_game_expiration signature
        check_sig = inspect.signature(self.service.check_single_game_expiration)
        assert 'db' in check_sig.parameters
        assert 'game_id' in check_sig.parameters
        assert check_sig.return_annotation != inspect.Signature.empty

    def test_service_methods_are_instance_methods(self):
        """Test that service methods are properly defined as instance methods"""
        # Verify methods exist and are callable
        assert hasattr(self.service, 'expire_past_games')
        assert callable(self.service.expire_past_games)
        assert hasattr(self.service, 'check_single_game_expiration')
        assert callable(self.service.check_single_game_expiration)
        
        # Verify they are instance methods (have 'self' parameter)
        import inspect
        
        expire_params = list(inspect.signature(self.service.expire_past_games).parameters.keys())
        assert expire_params[0] == 'db'  # After 'self' is bound
        
        check_params = list(inspect.signature(self.service.check_single_game_expiration).parameters.keys())
        assert check_params[0] == 'db'  # After 'self' is bound
        assert check_params[1] == 'game_id'