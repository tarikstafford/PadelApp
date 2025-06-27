from typing import List, Optional
from app.models.user import User
from app.models.tournament import TournamentMatch

class EloRatingService:
    """
    A service for calculating ELO rating changes after games.
    """
    K_FACTOR = 32
    TOURNAMENT_K_FACTOR = 40  # Higher K-factor for tournament matches

    @staticmethod
    def calculate_expected_score(team_rating: float, opponent_rating: float) -> float:
        """
        Calculates the expected score (probability of winning) for a team.
        
        Args:
            team_rating: The average ELO rating of the team.
            opponent_rating: The average ELO rating of the opponent team.
            
        Returns:
            The expected score, a value between 0 and 1.
        """
        return 1 / (1 + 10 ** ((opponent_rating - team_rating) / 400))

    @staticmethod
    def _calculate_team_rating(team: List[User]) -> float:
        """
        Calculates the average ELO rating for a team.
        """
        if not team:
            return 0.0
        return sum(player.elo_rating for player in team) / len(team)

    @classmethod
    def update_ratings(cls, team_a: List[User], team_b: List[User], score_a: float, score_b: float, is_tournament: bool = False):
        """
        Updates the ELO ratings for all players based on the game outcome.
        
        Args:
            team_a: List of players in team A
            team_b: List of players in team B
            score_a: Score of team A
            score_b: Score of team B
            is_tournament: Whether this is a tournament match (affects K-factor)
        """
        team_a_rating = cls._calculate_team_rating(team_a)
        team_b_rating = cls._calculate_team_rating(team_b)

        expected_a = cls.calculate_expected_score(team_a_rating, team_b_rating)
        expected_b = cls.calculate_expected_score(team_b_rating, team_a_rating)

        # Determine actual scores (1 for win, 0 for loss, 0.5 for draw)
        if score_a > score_b:
            actual_a, actual_b = 1.0, 0.0
        elif score_b > score_a:
            actual_a, actual_b = 0.0, 1.0
        else:
            actual_a, actual_b = 0.5, 0.5

        k_factor = cls.TOURNAMENT_K_FACTOR if is_tournament else cls.K_FACTOR
        rating_change_a = cls.calculate_rating_change(expected_a, actual_a, k_factor)
        rating_change_b = cls.calculate_rating_change(expected_b, actual_b, k_factor)

        for player in team_a:
            player.elo_rating += rating_change_a
            player.elo_rating = max(1.0, min(player.elo_rating, 7.0))
        for player in team_b:
            player.elo_rating += rating_change_b
            player.elo_rating = max(1.0, min(player.elo_rating, 7.0))

    @classmethod
    def calculate_rating_change(cls, expected_score: float, actual_score: float, k_factor: Optional[float] = None) -> float:
        """
        Calculates the change in a player's ELO rating.
        
        Args:
            expected_score: The expected score from calculate_expected_score.
            actual_score: The actual outcome of the game (1 for a win, 0.5 for a draw, 0 for a loss).
            k_factor: The K-factor to use (defaults to K_FACTOR if not provided).
            
        Returns:
            The amount the player's ELO rating should change.
        """
        if k_factor is None:
            k_factor = cls.K_FACTOR
        return k_factor * (actual_score - expected_score)

    @classmethod
    def update_tournament_match_ratings(cls, tournament_match: TournamentMatch, db):
        """
        Updates ELO ratings for players after a tournament match is completed.
        
        Args:
            tournament_match: The completed tournament match
            db: Database session
        """
        if tournament_match.status != "COMPLETED" or not tournament_match.winning_team_id:
            return

        # Get the teams and their players
        team1 = tournament_match.team1
        team2 = tournament_match.team2
        
        if not team1 or not team2:
            return

        team1_players = team1.team.players
        team2_players = team2.team.players

        # Update ratings with tournament K-factor
        cls.update_ratings(
            team_a=team1_players,
            team_b=team2_players,
            score_a=tournament_match.team1_score or 0,
            score_b=tournament_match.team2_score or 0,
            is_tournament=True
        )
        
        # Commit the changes to the database
        db.commit()

# This is a placeholder for the full implementation that will be built up
# through the subtasks.
elo_rating_service = EloRatingService() 