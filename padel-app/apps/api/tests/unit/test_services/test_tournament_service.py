import pytest
import math
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict, Any

from app.services.tournament_service import TournamentService, tournament_service
from app.models.tournament import (
    Tournament, TournamentTeam, TournamentMatch, TournamentCategoryConfig,
    TournamentType, MatchStatus, TournamentStatus
)
from app.schemas.tournament_schemas import TournamentBracket, BracketNode


class TestTournamentService:
    
    @pytest.fixture
    def tournament_service_instance(self):
        return TournamentService()
    
    @pytest.fixture
    def mock_db(self):
        return Mock(spec=Session)
    
    @pytest.fixture
    def mock_tournament(self):
        tournament = Mock(spec=Tournament)
        tournament.id = 1
        tournament.tournament_type = TournamentType.SINGLE_ELIMINATION
        tournament.start_date = datetime(2024, 1, 15, 9, 0)
        return tournament
    
    @pytest.fixture
    def mock_category_config(self):
        config = Mock(spec=TournamentCategoryConfig)
        config.id = 1
        config.category = "MIXED"
        return config
    
    @pytest.fixture
    def mock_teams(self):
        teams = []
        for i in range(4):
            team = Mock(spec=TournamentTeam)
            team.id = i + 1
            team.average_elo = 4.0 - (i * 0.5)  # Descending ELO ratings
            team.seed = None
            team.team = Mock()
            team.team.name = f"Team {i + 1}"
            teams.append(team)
        return teams


class TestGenerateBracket:
    def test_generate_bracket_tournament_not_found(self, tournament_service_instance, mock_db):
        with patch('app.services.tournament_service.tournament_crud.get_tournament', return_value=None):
            result = tournament_service_instance.generate_bracket(mock_db, 999, 1)
            assert result is None

    def test_generate_bracket_category_config_not_found(self, tournament_service_instance, mock_db, mock_tournament):
        with patch('app.services.tournament_service.tournament_crud.get_tournament', return_value=mock_tournament):
            mock_db.query.return_value.filter.return_value.first.return_value = None
            
            result = tournament_service_instance.generate_bracket(mock_db, 1, 999)
            assert result is None

    def test_generate_bracket_no_teams(self, tournament_service_instance, mock_db, mock_tournament, mock_category_config):
        with patch('app.services.tournament_service.tournament_crud.get_tournament', return_value=mock_tournament):
            mock_db.query.return_value.filter.return_value.first.return_value = mock_category_config
            
            with patch('app.services.tournament_service.tournament_crud.get_tournament_teams', return_value=[]):
                result = tournament_service_instance.generate_bracket(mock_db, 1, 1)
                assert result is None

    def test_generate_bracket_seeds_teams_by_elo(self, tournament_service_instance, mock_db, mock_tournament, mock_category_config, mock_teams):
        with patch('app.services.tournament_service.tournament_crud.get_tournament', return_value=mock_tournament):
            mock_db.query.return_value.filter.return_value.first.return_value = mock_category_config
            
            with patch('app.services.tournament_service.tournament_crud.get_tournament_teams', return_value=mock_teams):
                with patch.object(tournament_service_instance, '_generate_single_elimination_bracket', return_value=Mock()) as mock_generate:
                    result = tournament_service_instance.generate_bracket(mock_db, 1, 1)
                    
                    # Verify teams were seeded correctly
                    for i, team in enumerate(mock_teams):
                        assert team.seed == i + 1
                    
                    mock_db.commit.assert_called_once()

    def test_generate_bracket_single_elimination(self, tournament_service_instance, mock_db, mock_tournament, mock_category_config, mock_teams):
        mock_tournament.tournament_type = TournamentType.SINGLE_ELIMINATION
        
        with patch('app.services.tournament_service.tournament_crud.get_tournament', return_value=mock_tournament):
            mock_db.query.return_value.filter.return_value.first.return_value = mock_category_config
            
            with patch('app.services.tournament_service.tournament_crud.get_tournament_teams', return_value=mock_teams):
                with patch.object(tournament_service_instance, '_generate_single_elimination_bracket', return_value=Mock()) as mock_generate:
                    result = tournament_service_instance.generate_bracket(mock_db, 1, 1)
                    
                    mock_generate.assert_called_once_with(mock_db, mock_tournament, mock_category_config, mock_teams)

    def test_generate_bracket_double_elimination(self, tournament_service_instance, mock_db, mock_tournament, mock_category_config, mock_teams):
        mock_tournament.tournament_type = TournamentType.DOUBLE_ELIMINATION
        
        with patch('app.services.tournament_service.tournament_crud.get_tournament', return_value=mock_tournament):
            mock_db.query.return_value.filter.return_value.first.return_value = mock_category_config
            
            with patch('app.services.tournament_service.tournament_crud.get_tournament_teams', return_value=mock_teams):
                with patch.object(tournament_service_instance, '_generate_double_elimination_bracket', return_value=Mock()) as mock_generate:
                    result = tournament_service_instance.generate_bracket(mock_db, 1, 1)
                    
                    mock_generate.assert_called_once_with(mock_db, mock_tournament, mock_category_config, mock_teams)

    def test_generate_bracket_americano(self, tournament_service_instance, mock_db, mock_tournament, mock_category_config, mock_teams):
        mock_tournament.tournament_type = TournamentType.AMERICANO
        
        with patch('app.services.tournament_service.tournament_crud.get_tournament', return_value=mock_tournament):
            mock_db.query.return_value.filter.return_value.first.return_value = mock_category_config
            
            with patch('app.services.tournament_service.tournament_crud.get_tournament_teams', return_value=mock_teams):
                with patch.object(tournament_service_instance, '_generate_americano_bracket', return_value=Mock()) as mock_generate:
                    result = tournament_service_instance.generate_bracket(mock_db, 1, 1)
                    
                    mock_generate.assert_called_once_with(mock_db, mock_tournament, mock_category_config, mock_teams)


class TestGenerateSingleEliminationBracket:
    def test_generate_single_elimination_bracket_four_teams(self, tournament_service_instance, mock_db, mock_tournament, mock_category_config, mock_teams):
        # Mock create_match to return different matches
        mock_matches = []
        for i in range(6):  # 4 teams = 3 matches total (2 in round 1, 1 in round 2)
            match = Mock()
            match.id = i + 1
            mock_matches.append(match)
        
        with patch('app.services.tournament_service.tournament_crud.create_match', side_effect=mock_matches):
            result = tournament_service_instance._generate_single_elimination_bracket(
                mock_db, mock_tournament, mock_category_config, mock_teams
            )
            
            assert isinstance(result, TournamentBracket)
            assert result.tournament_id == mock_tournament.id
            assert result.category == mock_category_config.category
            assert result.tournament_type == mock_tournament.tournament_type
            assert result.total_rounds == 2  # 4 teams = 2 rounds
            assert len(result.rounds) == 2
            assert len(result.rounds[1]) == 2  # 2 matches in round 1
            assert len(result.rounds[2]) == 1  # 1 match in round 2

    def test_generate_single_elimination_bracket_calculates_correct_bracket_size(self, tournament_service_instance, mock_db, mock_tournament, mock_category_config):
        # Test with 3 teams - should create bracket size of 4 (next power of 2)
        teams = mock_teams[:3]
        
        mock_matches = [Mock(id=i) for i in range(10)]
        
        with patch('app.services.tournament_service.tournament_crud.create_match', side_effect=mock_matches):
            result = tournament_service_instance._generate_single_elimination_bracket(
                mock_db, mock_tournament, mock_category_config, teams
            )
            
            assert result.total_rounds == 2  # log2(4) = 2

    def test_generate_single_elimination_bracket_creates_correct_matches(self, tournament_service_instance, mock_db, mock_tournament, mock_category_config, mock_teams):
        mock_matches = [Mock(id=i) for i in range(10)]
        
        with patch('app.services.tournament_service.tournament_crud.create_match', side_effect=mock_matches) as mock_create:
            result = tournament_service_instance._generate_single_elimination_bracket(
                mock_db, mock_tournament, mock_category_config, mock_teams
            )
            
            # Should create 3 matches total for 4 teams (2 + 1)
            assert mock_create.call_count == 3

    def test_generate_single_elimination_bracket_handles_byes(self, tournament_service_instance, mock_db, mock_tournament, mock_category_config):
        # Test with 3 teams - one team should get a bye
        teams = mock_teams[:3]
        
        mock_matches = [Mock(id=i) for i in range(10)]
        
        with patch('app.services.tournament_service.tournament_crud.create_match', side_effect=mock_matches):
            result = tournament_service_instance._generate_single_elimination_bracket(
                mock_db, mock_tournament, mock_category_config, teams
            )
            
            # Check that some matches have "BYE" teams
            first_round = result.rounds[1]
            bye_count = sum(1 for match in first_round if match.team1_name == "BYE" or match.team2_name == "BYE")
            assert bye_count > 0


class TestGenerateAmericanoBracket:
    def test_generate_americano_bracket_creates_round_robin(self, tournament_service_instance, mock_db, mock_tournament, mock_category_config, mock_teams):
        mock_matches = [Mock(id=i) for i in range(20)]
        
        with patch('app.services.tournament_service.tournament_crud.create_match', side_effect=mock_matches) as mock_create:
            result = tournament_service_instance._generate_americano_bracket(
                mock_db, mock_tournament, mock_category_config, mock_teams
            )
            
            # 4 teams should create 6 matches (each team plays every other team once)
            # C(4,2) = 6
            assert mock_create.call_count == 6
            assert isinstance(result, TournamentBracket)
            assert result.tournament_type == mock_tournament.tournament_type

    def test_generate_americano_bracket_splits_matches_into_rounds(self, tournament_service_instance, mock_db, mock_tournament, mock_category_config, mock_teams):
        mock_matches = [Mock(id=i) for i in range(20)]
        
        with patch('app.services.tournament_service.tournament_crud.create_match', side_effect=mock_matches):
            result = tournament_service_instance._generate_americano_bracket(
                mock_db, mock_tournament, mock_category_config, mock_teams
            )
            
            # Should have multiple rounds with up to 4 matches per round
            total_matches = sum(len(round_matches) for round_matches in result.rounds.values())
            assert total_matches == 6  # C(4,2) = 6

    def test_generate_americano_bracket_all_teams_play_each_other(self, tournament_service_instance, mock_db, mock_tournament, mock_category_config, mock_teams):
        mock_matches = [Mock(id=i) for i in range(20)]
        
        with patch('app.services.tournament_service.tournament_crud.create_match', side_effect=mock_matches):
            result = tournament_service_instance._generate_americano_bracket(
                mock_db, mock_tournament, mock_category_config, mock_teams
            )
            
            # Collect all team pairs
            team_pairs = set()
            for round_matches in result.rounds.values():
                for match in round_matches:
                    pair = tuple(sorted([match.team1_id, match.team2_id]))
                    team_pairs.add(pair)
            
            # Should have 6 unique pairs for 4 teams
            assert len(team_pairs) == 6


class TestCreateSeededPairs:
    def test_create_seeded_pairs_standard_seeding(self, tournament_service_instance, mock_teams):
        bracket_size = 4
        pairs = tournament_service_instance._create_seeded_pairs(mock_teams, bracket_size)
        
        assert len(pairs) == 2  # bracket_size // 2
        
        # First pair should be seed 1 vs seed 4
        assert pairs[0][0] == mock_teams[0]  # Seed 1
        assert pairs[0][1] == mock_teams[3]  # Seed 4
        
        # Second pair should be seed 2 vs seed 3
        assert pairs[1][0] == mock_teams[1]  # Seed 2
        assert pairs[1][1] == mock_teams[2]  # Seed 3

    def test_create_seeded_pairs_with_byes(self, tournament_service_instance, mock_teams):
        # Test with 3 teams but bracket size 4
        teams = mock_teams[:3]
        bracket_size = 4
        
        pairs = tournament_service_instance._create_seeded_pairs(teams, bracket_size)
        
        assert len(pairs) == 2
        # One of the pairs should have a None team (bye)
        none_count = sum(1 for pair in pairs for team in pair if team is None)
        assert none_count == 1

    def test_create_seeded_pairs_large_bracket(self, tournament_service_instance):
        # Create 8 teams for testing
        teams = []
        for i in range(8):
            team = Mock()
            team.id = i + 1
            teams.append(team)
        
        bracket_size = 8
        pairs = tournament_service_instance._create_seeded_pairs(teams, bracket_size)
        
        assert len(pairs) == 4
        # Check standard tournament seeding pattern
        assert pairs[0][0] == teams[0]  # 1 vs 8
        assert pairs[0][1] == teams[7]
        assert pairs[1][0] == teams[1]  # 2 vs 7
        assert pairs[1][1] == teams[6]


class TestAdvanceWinner:
    def test_advance_winner_match_not_found(self, tournament_service_instance, mock_db):
        with patch('app.services.tournament_service.tournament_crud.get_match', return_value=None):
            result = tournament_service_instance.advance_winner(mock_db, 999, 1)
            assert result is False

    def test_advance_winner_updates_current_match(self, tournament_service_instance, mock_db):
        mock_match = Mock()
        mock_match.winner_advances_to_match_id = None
        
        with patch('app.services.tournament_service.tournament_crud.get_match', return_value=mock_match):
            with patch('app.services.tournament_service.tournament_crud.update_match') as mock_update:
                result = tournament_service_instance.advance_winner(mock_db, 1, 5)
                
                assert result is True
                mock_update.assert_called()

    def test_advance_winner_advances_to_next_match_team1_slot(self, tournament_service_instance, mock_db):
        mock_match = Mock()
        mock_match.winner_advances_to_match_id = 2
        
        mock_next_match = Mock()
        mock_next_match.id = 2
        mock_next_match.team1_id = None
        mock_next_match.team2_id = 3
        
        with patch('app.services.tournament_service.tournament_crud.get_match', side_effect=[mock_match, mock_next_match]):
            with patch('app.services.tournament_service.tournament_crud.update_match') as mock_update:
                result = tournament_service_instance.advance_winner(mock_db, 1, 5)
                
                assert result is True
                # Should be called twice: once for current match, once for next match
                assert mock_update.call_count == 2

    def test_advance_winner_advances_to_next_match_team2_slot(self, tournament_service_instance, mock_db):
        mock_match = Mock()
        mock_match.winner_advances_to_match_id = 2
        
        mock_next_match = Mock()
        mock_next_match.id = 2
        mock_next_match.team1_id = 3
        mock_next_match.team2_id = None
        
        with patch('app.services.tournament_service.tournament_crud.get_match', side_effect=[mock_match, mock_next_match]):
            with patch('app.services.tournament_service.tournament_crud.update_match') as mock_update:
                result = tournament_service_instance.advance_winner(mock_db, 1, 5)
                
                assert result is True
                assert mock_update.call_count == 2

    def test_advance_winner_no_next_match(self, tournament_service_instance, mock_db):
        mock_match = Mock()
        mock_match.winner_advances_to_match_id = 2
        
        with patch('app.services.tournament_service.tournament_crud.get_match', side_effect=[mock_match, None]):
            with patch('app.services.tournament_service.tournament_crud.update_match') as mock_update:
                result = tournament_service_instance.advance_winner(mock_db, 1, 5)
                
                assert result is True
                # Should only update current match
                assert mock_update.call_count == 1


class TestScheduleMatches:
    def test_schedule_matches_tournament_not_found(self, tournament_service_instance, mock_db):
        with patch('app.services.tournament_service.tournament_crud.get_tournament', return_value=None):
            result = tournament_service_instance.schedule_matches(mock_db, 999, {})
            assert result is False

    def test_schedule_matches_success(self, tournament_service_instance, mock_db, mock_tournament):
        # Mock tournament with court bookings
        mock_booking = Mock()
        mock_booking.court_id = 1
        mock_tournament.court_bookings = [mock_booking]
        
        # Mock matches
        mock_match1 = Mock()
        mock_match1.id = 1
        mock_match1.round_number = 1
        mock_match1.team1_id = 1
        mock_match1.team2_id = 2
        
        mock_match2 = Mock()
        mock_match2.id = 2
        mock_match2.round_number = 1
        mock_match2.team1_id = 3
        mock_match2.team2_id = 4
        
        mock_matches = [mock_match1, mock_match2]
        
        with patch('app.services.tournament_service.tournament_crud.get_tournament', return_value=mock_tournament):
            with patch('app.services.tournament_service.tournament_crud.get_tournament_matches', return_value=mock_matches):
                with patch('app.services.tournament_service.tournament_crud.update_match') as mock_update:
                    result = tournament_service_instance.schedule_matches(mock_db, 1, {})
                    
                    assert result is True
                    # Should update both matches with scheduling info
                    assert mock_update.call_count == 2

    def test_schedule_matches_skips_incomplete_matches(self, tournament_service_instance, mock_db, mock_tournament):
        mock_booking = Mock()
        mock_booking.court_id = 1
        mock_tournament.court_bookings = [mock_booking]
        
        # Mock match with missing team
        mock_match = Mock()
        mock_match.id = 1
        mock_match.round_number = 1
        mock_match.team1_id = 1
        mock_match.team2_id = None  # Missing team
        
        with patch('app.services.tournament_service.tournament_crud.get_tournament', return_value=mock_tournament):
            with patch('app.services.tournament_service.tournament_crud.get_tournament_matches', return_value=[mock_match]):
                with patch('app.services.tournament_service.tournament_crud.update_match') as mock_update:
                    result = tournament_service_instance.schedule_matches(mock_db, 1, {})
                    
                    assert result is True
                    # Should not update match with missing team
                    mock_update.assert_not_called()

    def test_schedule_matches_multiple_courts(self, tournament_service_instance, mock_db, mock_tournament):
        # Mock tournament with multiple courts
        mock_bookings = [Mock(court_id=1), Mock(court_id=2)]
        mock_tournament.court_bookings = mock_bookings
        
        # Mock multiple matches
        mock_matches = []
        for i in range(4):
            match = Mock()
            match.id = i + 1
            match.round_number = 1
            match.team1_id = (i * 2) + 1
            match.team2_id = (i * 2) + 2
            mock_matches.append(match)
        
        with patch('app.services.tournament_service.tournament_crud.get_tournament', return_value=mock_tournament):
            with patch('app.services.tournament_service.tournament_crud.get_tournament_matches', return_value=mock_matches):
                with patch('app.services.tournament_service.tournament_crud.update_match') as mock_update:
                    result = tournament_service_instance.schedule_matches(mock_db, 1, {})
                    
                    assert result is True
                    # Should schedule all 4 matches
                    assert mock_update.call_count == 4


class TestGetTournamentBracket:
    def test_get_tournament_bracket_tournament_not_found(self, tournament_service_instance, mock_db):
        with patch('app.services.tournament_service.tournament_crud.get_tournament', return_value=None):
            result = tournament_service_instance.get_tournament_bracket(mock_db, 999, 1)
            assert result is None

    def test_get_tournament_bracket_category_config_not_found(self, tournament_service_instance, mock_db, mock_tournament):
        with patch('app.services.tournament_service.tournament_crud.get_tournament', return_value=mock_tournament):
            mock_db.query.return_value.filter.return_value.first.return_value = None
            
            result = tournament_service_instance.get_tournament_bracket(mock_db, 1, 999)
            assert result is None

    def test_get_tournament_bracket_success(self, tournament_service_instance, mock_db, mock_tournament, mock_category_config):
        # Mock matches
        mock_match = Mock()
        mock_match.id = 1
        mock_match.round_number = 1
        mock_match.match_number = 1
        mock_match.team1_id = 1
        mock_match.team2_id = 2
        mock_match.team1 = Mock()
        mock_match.team1.team = Mock(name="Team 1")
        mock_match.team2 = Mock()
        mock_match.team2.team = Mock(name="Team 2")
        mock_match.winning_team_id = None
        mock_match.status = MatchStatus.SCHEDULED
        mock_match.team1_score = None
        mock_match.team2_score = None
        
        with patch('app.services.tournament_service.tournament_crud.get_tournament', return_value=mock_tournament):
            mock_db.query.return_value.filter.return_value.first.return_value = mock_category_config
            
            with patch('app.services.tournament_service.tournament_crud.get_tournament_matches', return_value=[mock_match]):
                result = tournament_service_instance.get_tournament_bracket(mock_db, 1, 1)
                
                assert isinstance(result, TournamentBracket)
                assert result.tournament_id == 1
                assert result.category == mock_category_config.category
                assert result.tournament_type == mock_tournament.tournament_type
                assert len(result.rounds) == 1
                assert len(result.rounds[1]) == 1

    def test_get_tournament_bracket_handles_tbd_teams(self, tournament_service_instance, mock_db, mock_tournament, mock_category_config):
        # Mock match with no teams assigned
        mock_match = Mock()
        mock_match.id = 1
        mock_match.round_number = 1
        mock_match.match_number = 1
        mock_match.team1_id = None
        mock_match.team2_id = None
        mock_match.team1 = None
        mock_match.team2 = None
        mock_match.winning_team_id = None
        mock_match.status = MatchStatus.SCHEDULED
        mock_match.team1_score = None
        mock_match.team2_score = None
        
        with patch('app.services.tournament_service.tournament_crud.get_tournament', return_value=mock_tournament):
            mock_db.query.return_value.filter.return_value.first.return_value = mock_category_config
            
            with patch('app.services.tournament_service.tournament_crud.get_tournament_matches', return_value=[mock_match]):
                result = tournament_service_instance.get_tournament_bracket(mock_db, 1, 1)
                
                assert result.rounds[1][0].team1_name == "TBD"
                assert result.rounds[1][0].team2_name == "TBD"


class TestFinalizeTournament:
    def test_finalize_tournament_tournament_not_found(self, tournament_service_instance, mock_db):
        with patch('app.services.tournament_service.tournament_crud.get_tournament', return_value=None):
            result = tournament_service_instance.finalize_tournament(mock_db, 999)
            assert result is False

    def test_finalize_tournament_success(self, tournament_service_instance, mock_db, mock_tournament):
        # Mock category config
        mock_category = Mock()
        mock_category.id = 1
        mock_category.category = "MIXED"
        mock_tournament.categories = [mock_category]
        
        # Mock final match
        mock_final_match = Mock()
        mock_final_match.round_number = 2
        mock_final_match.winning_team_id = 1
        mock_final_match.status = MatchStatus.COMPLETED
        
        # Mock winning team
        mock_winning_team = Mock()
        mock_winning_team.team_id = 1
        mock_winning_team.team = Mock()
        mock_player = Mock()
        mock_player.id = 1
        mock_winning_team.team.players = [mock_player]
        
        with patch('app.services.tournament_service.tournament_crud.get_tournament', return_value=mock_tournament):
            with patch('app.services.tournament_service.tournament_crud.update_tournament') as mock_update_tournament:
                with patch('app.services.tournament_service.tournament_crud.get_tournament_matches', return_value=[mock_final_match]):
                    mock_db.query.return_value.filter.return_value.first.return_value = mock_winning_team
                    
                    with patch('app.services.tournament_service.tournament_crud.award_trophy') as mock_award:
                        result = tournament_service_instance.finalize_tournament(mock_db, 1)
                        
                        assert result is True
                        mock_update_tournament.assert_called_once()
                        mock_award.assert_called_once()

    def test_finalize_tournament_no_completed_final(self, tournament_service_instance, mock_db, mock_tournament):
        # Mock category config
        mock_category = Mock()
        mock_category.id = 1
        mock_category.category = "MIXED"
        mock_tournament.categories = [mock_category]
        
        # Mock final match that's not completed
        mock_final_match = Mock()
        mock_final_match.round_number = 2
        mock_final_match.winning_team_id = None
        mock_final_match.status = MatchStatus.SCHEDULED
        
        with patch('app.services.tournament_service.tournament_crud.get_tournament', return_value=mock_tournament):
            with patch('app.services.tournament_service.tournament_crud.update_tournament') as mock_update_tournament:
                with patch('app.services.tournament_service.tournament_crud.get_tournament_matches', return_value=[mock_final_match]):
                    with patch('app.services.tournament_service.tournament_crud.award_trophy') as mock_award:
                        result = tournament_service_instance.finalize_tournament(mock_db, 1)
                        
                        assert result is True
                        mock_update_tournament.assert_called_once()
                        # Should not award trophy for incomplete match
                        mock_award.assert_not_called()

    def test_finalize_tournament_multiple_categories(self, tournament_service_instance, mock_db, mock_tournament):
        # Mock multiple category configs
        mock_categories = []
        for i in range(2):
            category = Mock()
            category.id = i + 1
            category.category = f"CATEGORY_{i + 1}"
            mock_categories.append(category)
        mock_tournament.categories = mock_categories
        
        # Mock final matches for each category
        mock_matches = []
        for i in range(2):
            match = Mock()
            match.round_number = 2
            match.winning_team_id = i + 1
            match.status = MatchStatus.COMPLETED
            mock_matches.append(match)
        
        # Mock winning teams
        mock_winning_teams = []
        for i in range(2):
            team = Mock()
            team.team_id = i + 1
            team.team = Mock()
            player = Mock()
            player.id = i + 1
            team.team.players = [player]
            mock_winning_teams.append(team)
        
        with patch('app.services.tournament_service.tournament_crud.get_tournament', return_value=mock_tournament):
            with patch('app.services.tournament_service.tournament_crud.update_tournament') as mock_update_tournament:
                with patch('app.services.tournament_service.tournament_crud.get_tournament_matches', side_effect=[mock_matches[:1], mock_matches[1:]]):
                    mock_db.query.return_value.filter.return_value.first.side_effect = mock_winning_teams
                    
                    with patch('app.services.tournament_service.tournament_crud.award_trophy') as mock_award:
                        result = tournament_service_instance.finalize_tournament(mock_db, 1)
                        
                        assert result is True
                        mock_update_tournament.assert_called_once()
                        # Should award trophies for both categories
                        assert mock_award.call_count == 2


class TestTournamentServiceSingleton:
    def test_tournament_service_instance_exists(self):
        """Test that the tournament_service singleton instance exists."""
        assert tournament_service is not None
        assert isinstance(tournament_service, TournamentService)

    def test_tournament_service_singleton_consistency(self):
        """Test that multiple references to tournament_service return the same instance."""
        from app.services.tournament_service import tournament_service as service1
        from app.services.tournament_service import tournament_service as service2
        
        assert service1 is service2


class TestTournamentServiceEdgeCases:
    def test_generate_bracket_with_one_team(self, tournament_service_instance, mock_db, mock_tournament, mock_category_config):
        # Test with only one team
        teams = mock_teams[:1]
        
        with patch('app.services.tournament_service.tournament_crud.get_tournament', return_value=mock_tournament):
            mock_db.query.return_value.filter.return_value.first.return_value = mock_category_config
            
            with patch('app.services.tournament_service.tournament_crud.get_tournament_teams', return_value=teams):
                mock_matches = [Mock(id=i) for i in range(5)]
                
                with patch('app.services.tournament_service.tournament_crud.create_match', side_effect=mock_matches):
                    result = tournament_service_instance.generate_bracket(mock_db, 1, 1)
                    
                    assert isinstance(result, TournamentBracket)
                    # With 1 team, bracket size is 2, so 1 round
                    assert result.total_rounds == 1

    def test_generate_bracket_with_large_number_of_teams(self, tournament_service_instance, mock_db, mock_tournament, mock_category_config):
        # Test with 16 teams
        teams = []
        for i in range(16):
            team = Mock()
            team.id = i + 1
            team.average_elo = 4.0
            team.seed = None
            team.team = Mock(name=f"Team {i + 1}")
            teams.append(team)
        
        with patch('app.services.tournament_service.tournament_crud.get_tournament', return_value=mock_tournament):
            mock_db.query.return_value.filter.return_value.first.return_value = mock_category_config
            
            with patch('app.services.tournament_service.tournament_crud.get_tournament_teams', return_value=teams):
                mock_matches = [Mock(id=i) for i in range(50)]
                
                with patch('app.services.tournament_service.tournament_crud.create_match', side_effect=mock_matches):
                    result = tournament_service_instance.generate_bracket(mock_db, 1, 1)
                    
                    assert isinstance(result, TournamentBracket)
                    # 16 teams = 4 rounds (log2(16) = 4)
                    assert result.total_rounds == 4

    def test_advance_winner_both_slots_filled(self, tournament_service_instance, mock_db):
        mock_match = Mock()
        mock_match.winner_advances_to_match_id = 2
        
        mock_next_match = Mock()
        mock_next_match.id = 2
        mock_next_match.team1_id = 3  # Both slots filled
        mock_next_match.team2_id = 4
        
        with patch('app.services.tournament_service.tournament_crud.get_match', side_effect=[mock_match, mock_next_match]):
            with patch('app.services.tournament_service.tournament_crud.update_match') as mock_update:
                result = tournament_service_instance.advance_winner(mock_db, 1, 5)
                
                assert result is True
                # Should only update current match since next match is full
                assert mock_update.call_count == 1

    def test_americano_bracket_with_odd_number_of_teams(self, tournament_service_instance, mock_db, mock_tournament, mock_category_config):
        # Test with 3 teams
        teams = mock_teams[:3]
        
        mock_matches = [Mock(id=i) for i in range(10)]
        
        with patch('app.services.tournament_service.tournament_crud.create_match', side_effect=mock_matches):
            result = tournament_service_instance._generate_americano_bracket(
                mock_db, mock_tournament, mock_category_config, teams
            )
            
            # 3 teams should create 3 matches (C(3,2) = 3)
            total_matches = sum(len(round_matches) for round_matches in result.rounds.values())
            assert total_matches == 3


class TestTournamentServiceIntegration:
    def test_full_tournament_workflow(self, tournament_service_instance, mock_db, mock_tournament, mock_category_config, mock_teams):
        """Integration test for complete tournament workflow."""
        
        # 1. Generate bracket
        with patch('app.services.tournament_service.tournament_crud.get_tournament', return_value=mock_tournament):
            mock_db.query.return_value.filter.return_value.first.return_value = mock_category_config
            
            with patch('app.services.tournament_service.tournament_crud.get_tournament_teams', return_value=mock_teams):
                mock_matches = [Mock(id=i) for i in range(10)]
                
                with patch('app.services.tournament_service.tournament_crud.create_match', side_effect=mock_matches):
                    bracket = tournament_service_instance.generate_bracket(mock_db, 1, 1)
                    
                    assert bracket is not None
        
        # 2. Schedule matches
        mock_tournament.court_bookings = [Mock(court_id=1)]
        mock_scheduled_matches = [Mock(id=1, round_number=1, team1_id=1, team2_id=2)]
        
        with patch('app.services.tournament_service.tournament_crud.get_tournament', return_value=mock_tournament):
            with patch('app.services.tournament_service.tournament_crud.get_tournament_matches', return_value=mock_scheduled_matches):
                with patch('app.services.tournament_service.tournament_crud.update_match'):
                    scheduled = tournament_service_instance.schedule_matches(mock_db, 1, {})
                    
                    assert scheduled is True
        
        # 3. Advance winner
        mock_match = Mock()
        mock_match.winner_advances_to_match_id = None
        
        with patch('app.services.tournament_service.tournament_crud.get_match', return_value=mock_match):
            with patch('app.services.tournament_service.tournament_crud.update_match'):
                advanced = tournament_service_instance.advance_winner(mock_db, 1, 1)
                
                assert advanced is True
        
        # 4. Finalize tournament
        mock_tournament.categories = [mock_category_config]
        mock_final_match = Mock()
        mock_final_match.round_number = 2
        mock_final_match.winning_team_id = 1
        mock_final_match.status = MatchStatus.COMPLETED
        
        mock_winning_team = Mock()
        mock_winning_team.team = Mock()
        mock_winning_team.team.players = [Mock(id=1)]
        
        with patch('app.services.tournament_service.tournament_crud.get_tournament', return_value=mock_tournament):
            with patch('app.services.tournament_service.tournament_crud.update_tournament'):
                with patch('app.services.tournament_service.tournament_crud.get_tournament_matches', return_value=[mock_final_match]):
                    mock_db.query.return_value.filter.return_value.first.return_value = mock_winning_team
                    
                    with patch('app.services.tournament_service.tournament_crud.award_trophy'):
                        finalized = tournament_service_instance.finalize_tournament(mock_db, 1)
                        
                        assert finalized is True