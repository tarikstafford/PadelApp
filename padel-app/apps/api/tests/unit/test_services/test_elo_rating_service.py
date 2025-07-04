import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from app.services.elo_rating_service import EloRatingService, elo_rating_service
from app.models.user import User
from app.models.tournament import TournamentMatch


class TestEloRatingService:
    """Comprehensive test suite for EloRatingService"""

    def setup_method(self):
        """Set up test fixtures"""
        self.service = EloRatingService()
        self.mock_db = Mock(spec=Session)

    @pytest.mark.parametrize("team_rating, opponent_rating, expected_score", [
        (1500, 1500, 0.5),         # Equal ratings
        (1600, 1500, 0.64),        # Higher rated team
        (1500, 1600, 0.36),        # Lower rated team
        (2000, 1000, 0.99),        # Large rating difference
        (1000, 2000, 0.01),        # Large rating difference (inverted)
        (1400, 1400, 0.5),         # Different equal ratings
        (1800, 1200, 0.909),       # Large gap
        (1200, 1800, 0.091),       # Large gap (inverted)
    ])
    def test_calculate_expected_score(self, team_rating, opponent_rating, expected_score):
        """Test the calculate_expected_score method with various rating combinations"""
        score = EloRatingService.calculate_expected_score(team_rating, opponent_rating)
        assert score == pytest.approx(expected_score, abs=1e-2)

    def test_calculate_expected_score_extreme_values(self):
        """Test calculate_expected_score with extreme rating values"""
        # Test with very high rating difference
        score = EloRatingService.calculate_expected_score(3000, 500)
        assert score > 0.99
        
        # Test with very low rating difference
        score = EloRatingService.calculate_expected_score(500, 3000)
        assert score < 0.01

    @pytest.mark.parametrize("expected_score, actual_score, expected_change", [
        (0.5, 1, 16),          # Win against equal opponent
        (0.5, 0, -16),         # Loss against equal opponent
        (0.5, 0.5, 0),         # Draw against equal opponent
        (0.64, 1, 11.52),      # Expected win, and won
        (0.64, 0, -20.48),     # Expected win, but lost (upset)
        (0.36, 1, 20.48),      # Expected loss, but won (upset)
        (0.36, 0, -11.52),     # Expected loss, and lost
        (0.8, 1, 6.4),         # Strong favorite wins
        (0.2, 0, -6.4),        # Underdog loses
    ])
    def test_calculate_rating_change(self, expected_score, actual_score, expected_change):
        """Test the calculate_rating_change method"""
        change = EloRatingService.calculate_rating_change(expected_score, actual_score)
        assert change == pytest.approx(expected_change, abs=1e-2)

    def test_calculate_rating_change_with_custom_k_factor(self):
        """Test calculate_rating_change with custom K-factor"""
        expected_score = 0.5
        actual_score = 1
        custom_k_factor = 50
        
        change = EloRatingService.calculate_rating_change(expected_score, actual_score, custom_k_factor)
        expected_change = custom_k_factor * (actual_score - expected_score)
        
        assert change == pytest.approx(expected_change, abs=1e-2)

    def test_calculate_rating_change_tournament_k_factor(self):
        """Test calculate_rating_change with tournament K-factor"""
        expected_score = 0.5
        actual_score = 1
        
        change = EloRatingService.calculate_rating_change(expected_score, actual_score, EloRatingService.TOURNAMENT_K_FACTOR)
        expected_change = EloRatingService.TOURNAMENT_K_FACTOR * (actual_score - expected_score)
        
        assert change == pytest.approx(expected_change, abs=1e-2)

    def test_calculate_team_rating_single_player(self):
        """Test _calculate_team_rating with single player"""
        player = Mock()
        player.elo_rating = 1500
        team = [player]
        
        team_rating = EloRatingService._calculate_team_rating(team)
        assert team_rating == 1500

    def test_calculate_team_rating_multiple_players(self):
        """Test _calculate_team_rating with multiple players"""
        player1 = Mock()
        player1.elo_rating = 1500
        player2 = Mock()
        player2.elo_rating = 1600
        player3 = Mock()
        player3.elo_rating = 1400
        team = [player1, player2, player3]
        
        team_rating = EloRatingService._calculate_team_rating(team)
        assert team_rating == 1500  # (1500 + 1600 + 1400) / 3

    def test_calculate_team_rating_empty_team(self):
        """Test _calculate_team_rating with empty team"""
        team = []
        team_rating = EloRatingService._calculate_team_rating(team)
        assert team_rating == 0.0

    def test_calculate_team_rating_with_float_ratings(self):
        """Test _calculate_team_rating with float ratings"""
        player1 = Mock()
        player1.elo_rating = 1500.5
        player2 = Mock()
        player2.elo_rating = 1600.3
        team = [player1, player2]
        
        team_rating = EloRatingService._calculate_team_rating(team)
        assert team_rating == pytest.approx(1550.4, abs=1e-2)

    def test_update_ratings_team_a_wins(self):
        """Test update_ratings when team A wins"""
        player_a1 = Mock(elo_rating=4.0)
        player_a2 = Mock(elo_rating=4.0)
        team_a = [player_a1, player_a2]

        player_b1 = Mock(elo_rating=4.0)
        player_b2 = Mock(elo_rating=4.0)
        team_b = [player_b1, player_b2]

        EloRatingService.update_ratings(team_a, team_b, 1, 0)

        # Winners should gain rating
        assert player_a1.elo_rating > 4.0
        assert player_a2.elo_rating > 4.0
        
        # Losers should lose rating
        assert player_b1.elo_rating < 4.0
        assert player_b2.elo_rating < 4.0

    def test_update_ratings_team_b_wins(self):
        """Test update_ratings when team B wins"""
        player_a1 = Mock(elo_rating=4.0)
        player_a2 = Mock(elo_rating=4.0)
        team_a = [player_a1, player_a2]

        player_b1 = Mock(elo_rating=4.0)
        player_b2 = Mock(elo_rating=4.0)
        team_b = [player_b1, player_b2]

        EloRatingService.update_ratings(team_a, team_b, 0, 1)

        # Losers should lose rating
        assert player_a1.elo_rating < 4.0
        assert player_a2.elo_rating < 4.0
        
        # Winners should gain rating
        assert player_b1.elo_rating > 4.0
        assert player_b2.elo_rating > 4.0

    def test_update_ratings_draw(self):
        """Test update_ratings when game is a draw"""
        player_a1 = Mock(elo_rating=4.0)
        player_a2 = Mock(elo_rating=4.0)
        team_a = [player_a1, player_a2]

        player_b1 = Mock(elo_rating=4.0)
        player_b2 = Mock(elo_rating=4.0)
        team_b = [player_b1, player_b2]

        EloRatingService.update_ratings(team_a, team_b, 1, 1)

        # Both teams should have unchanged ratings (equal teams, equal scores)
        assert player_a1.elo_rating == 4.0
        assert player_a2.elo_rating == 4.0
        assert player_b1.elo_rating == 4.0
        assert player_b2.elo_rating == 4.0

    def test_update_ratings_upset_win(self):
        """Test update_ratings when lower-rated team wins (upset)"""
        player_a1 = Mock(elo_rating=3.0)
        player_a2 = Mock(elo_rating=3.0)
        team_a = [player_a1, player_a2]

        player_b1 = Mock(elo_rating=5.0)
        player_b2 = Mock(elo_rating=5.0)
        team_b = [player_b1, player_b2]

        EloRatingService.update_ratings(team_a, team_b, 1, 0)

        # Lower-rated team should gain more points
        assert player_a1.elo_rating > 3.0
        assert player_a2.elo_rating > 3.0
        
        # Higher-rated team should lose more points
        assert player_b1.elo_rating < 5.0
        assert player_b2.elo_rating < 5.0

    def test_update_ratings_tournament_mode(self):
        """Test update_ratings with tournament mode (higher K-factor)"""
        player_a1 = Mock(elo_rating=4.0)
        player_a2 = Mock(elo_rating=4.0)
        team_a = [player_a1, player_a2]

        player_b1 = Mock(elo_rating=4.0)
        player_b2 = Mock(elo_rating=4.0)
        team_b = [player_b1, player_b2]

        # Regular update
        EloRatingService.update_ratings(team_a, team_b, 1, 0, is_tournament=False)
        regular_rating_a = player_a1.elo_rating
        regular_rating_b = player_b1.elo_rating

        # Reset ratings
        player_a1.elo_rating = 4.0
        player_a2.elo_rating = 4.0
        player_b1.elo_rating = 4.0
        player_b2.elo_rating = 4.0

        # Tournament update
        EloRatingService.update_ratings(team_a, team_b, 1, 0, is_tournament=True)
        tournament_rating_a = player_a1.elo_rating
        tournament_rating_b = player_b1.elo_rating

        # Tournament changes should be larger
        assert abs(tournament_rating_a - 4.0) > abs(regular_rating_a - 4.0)
        assert abs(tournament_rating_b - 4.0) > abs(regular_rating_b - 4.0)

    def test_update_ratings_clamping_upper_bound(self):
        """Test that ratings are clamped to upper bound (7.0)"""
        player_a1 = Mock(elo_rating=6.9)
        team_a = [player_a1]
        
        player_b1 = Mock(elo_rating=1.1)
        team_b = [player_b1]

        # Large win that would push rating above 7.0
        EloRatingService.update_ratings(team_a, team_b, 1, 0)
        assert player_a1.elo_rating <= 7.0

    def test_update_ratings_clamping_lower_bound(self):
        """Test that ratings are clamped to lower bound (1.0)"""
        player_a1 = Mock(elo_rating=1.1)
        team_a = [player_a1]

        player_b1 = Mock(elo_rating=6.9)
        team_b = [player_b1]

        # Large loss that would push rating below 1.0
        EloRatingService.update_ratings(team_a, team_b, 0, 1)
        assert player_a1.elo_rating >= 1.0

    def test_update_ratings_extreme_clamping(self):
        """Test rating clamping with extreme values"""
        player_a1 = Mock(elo_rating=7.0)
        team_a = [player_a1]
        
        player_b1 = Mock(elo_rating=1.0)
        team_b = [player_b1]

        # Test upper bound
        EloRatingService.update_ratings(team_a, team_b, 1, 0)
        assert player_a1.elo_rating == 7.0

        # Test lower bound
        EloRatingService.update_ratings(team_a, team_b, 0, 1)
        assert player_b1.elo_rating == 1.0

    def test_update_ratings_empty_teams(self):
        """Test update_ratings with empty teams"""
        team_a = []
        team_b = []

        # Should handle empty teams gracefully
        EloRatingService.update_ratings(team_a, team_b, 1, 0)
        # No assertion needed, just verify no exception is raised

    def test_update_ratings_single_player_teams(self):
        """Test update_ratings with single player teams"""
        player_a1 = Mock(elo_rating=4.0)
        team_a = [player_a1]

        player_b1 = Mock(elo_rating=4.0)
        team_b = [player_b1]

        EloRatingService.update_ratings(team_a, team_b, 1, 0)

        assert player_a1.elo_rating > 4.0
        assert player_b1.elo_rating < 4.0

    def test_update_tournament_match_ratings_success(self):
        """Test successful tournament match rating update"""
        # Setup mock tournament match
        mock_match = Mock()
        mock_match.status = "COMPLETED"
        mock_match.winning_team_id = 1
        mock_match.team1_score = 6
        mock_match.team2_score = 4

        # Setup mock teams and players
        mock_player1 = Mock()
        mock_player1.elo_rating = 4.0
        mock_player2 = Mock()
        mock_player2.elo_rating = 4.0
        mock_player3 = Mock()
        mock_player3.elo_rating = 4.0
        mock_player4 = Mock()
        mock_player4.elo_rating = 4.0

        mock_team1 = Mock()
        mock_team1.team.players = [mock_player1, mock_player2]
        mock_team2 = Mock()
        mock_team2.team.players = [mock_player3, mock_player4]

        mock_match.team1 = mock_team1
        mock_match.team2 = mock_team2

        # Execute
        EloRatingService.update_tournament_match_ratings(mock_match, self.mock_db)

        # Verify ratings were updated
        assert mock_player1.elo_rating != 4.0
        assert mock_player2.elo_rating != 4.0
        assert mock_player3.elo_rating != 4.0
        assert mock_player4.elo_rating != 4.0

        # Verify database commit was called
        self.mock_db.commit.assert_called_once()

    def test_update_tournament_match_ratings_not_completed(self):
        """Test tournament match rating update when match is not completed"""
        mock_match = Mock()
        mock_match.status = "SCHEDULED"
        mock_match.winning_team_id = None

        # Execute
        EloRatingService.update_tournament_match_ratings(mock_match, self.mock_db)

        # Verify no commit was called
        self.mock_db.commit.assert_not_called()

    def test_update_tournament_match_ratings_no_winner(self):
        """Test tournament match rating update when no winner is set"""
        mock_match = Mock()
        mock_match.status = "COMPLETED"
        mock_match.winning_team_id = None

        # Execute
        EloRatingService.update_tournament_match_ratings(mock_match, self.mock_db)

        # Verify no commit was called
        self.mock_db.commit.assert_not_called()

    def test_update_tournament_match_ratings_missing_teams(self):
        """Test tournament match rating update when teams are missing"""
        mock_match = Mock()
        mock_match.status = "COMPLETED"
        mock_match.winning_team_id = 1
        mock_match.team1 = None
        mock_match.team2 = None

        # Execute
        EloRatingService.update_tournament_match_ratings(mock_match, self.mock_db)

        # Verify no commit was called
        self.mock_db.commit.assert_not_called()

    def test_update_tournament_match_ratings_one_team_missing(self):
        """Test tournament match rating update when one team is missing"""
        mock_match = Mock()
        mock_match.status = "COMPLETED"
        mock_match.winning_team_id = 1
        mock_match.team1 = Mock()
        mock_match.team2 = None

        # Execute
        EloRatingService.update_tournament_match_ratings(mock_match, self.mock_db)

        # Verify no commit was called
        self.mock_db.commit.assert_not_called()

    def test_update_tournament_match_ratings_null_scores(self):
        """Test tournament match rating update with null scores"""
        mock_match = Mock()
        mock_match.status = "COMPLETED"
        mock_match.winning_team_id = 1
        mock_match.team1_score = None
        mock_match.team2_score = None

        # Setup mock teams and players
        mock_player1 = Mock()
        mock_player1.elo_rating = 4.0
        mock_player2 = Mock()
        mock_player2.elo_rating = 4.0

        mock_team1 = Mock()
        mock_team1.team.players = [mock_player1]
        mock_team2 = Mock()
        mock_team2.team.players = [mock_player2]

        mock_match.team1 = mock_team1
        mock_match.team2 = mock_team2

        # Execute
        EloRatingService.update_tournament_match_ratings(mock_match, self.mock_db)

        # Verify it handles null scores (defaults to 0)
        self.mock_db.commit.assert_called_once()

    def test_k_factor_constants(self):
        """Test that K-factor constants are properly defined"""
        assert EloRatingService.K_FACTOR == 32
        assert EloRatingService.TOURNAMENT_K_FACTOR == 40
        assert EloRatingService.TOURNAMENT_K_FACTOR > EloRatingService.K_FACTOR

    def test_service_instance_singleton(self):
        """Test that the service instance is properly initialized"""
        assert elo_rating_service is not None
        assert isinstance(elo_rating_service, EloRatingService)

    def test_rating_change_symmetry(self):
        """Test that rating changes are symmetric for equal teams"""
        player_a = Mock(elo_rating=4.0)
        player_b = Mock(elo_rating=4.0)
        team_a = [player_a]
        team_b = [player_b]

        # Team A wins
        EloRatingService.update_ratings(team_a, team_b, 1, 0)
        
        rating_change_a = player_a.elo_rating - 4.0
        rating_change_b = player_b.elo_rating - 4.0

        # Changes should be equal and opposite
        assert abs(rating_change_a) == abs(rating_change_b)
        assert rating_change_a == -rating_change_b

    def test_rating_conservation(self):
        """Test that total rating points are conserved in the system"""
        player_a1 = Mock(elo_rating=4.0)
        player_a2 = Mock(elo_rating=4.0)
        team_a = [player_a1, player_a2]

        player_b1 = Mock(elo_rating=4.0)
        player_b2 = Mock(elo_rating=4.0)
        team_b = [player_b1, player_b2]

        # Calculate total rating before
        total_before = sum(p.elo_rating for p in team_a + team_b)

        # Update ratings
        EloRatingService.update_ratings(team_a, team_b, 1, 0)

        # Calculate total rating after
        total_after = sum(p.elo_rating for p in team_a + team_b)

        # Total should be conserved (within floating point precision)
        assert abs(total_before - total_after) < 1e-10

    def test_mathematical_properties(self):
        """Test mathematical properties of the ELO system"""
        # Test expected score sum equals 1
        team_rating = 1500
        opponent_rating = 1600
        
        expected_a = EloRatingService.calculate_expected_score(team_rating, opponent_rating)
        expected_b = EloRatingService.calculate_expected_score(opponent_rating, team_rating)
        
        assert abs(expected_a + expected_b - 1.0) < 1e-10

    def test_boundary_conditions(self):
        """Test boundary conditions for rating updates"""
        # Test with minimum possible ratings
        player_a = Mock(elo_rating=1.0)
        player_b = Mock(elo_rating=1.0)
        team_a = [player_a]
        team_b = [player_b]

        EloRatingService.update_ratings(team_a, team_b, 1, 0)
        
        assert player_a.elo_rating >= 1.0
        assert player_b.elo_rating >= 1.0

        # Test with maximum possible ratings
        player_c = Mock(elo_rating=7.0)
        player_d = Mock(elo_rating=7.0)
        team_c = [player_c]
        team_d = [player_d]

        EloRatingService.update_ratings(team_c, team_d, 1, 0)
        
        assert player_c.elo_rating <= 7.0
        assert player_d.elo_rating <= 7.0