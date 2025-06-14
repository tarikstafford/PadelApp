from typing import List
from app.models.user import User

class EloRatingService:
    """
    A service for calculating ELO rating changes after games.
    """
    K_FACTOR = 32

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
    def update_ratings(cls, team_a: List[User], team_b: List[User], score_a: float, score_b: float):
        """
        Updates the ELO ratings for all players based on the game outcome.
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

        rating_change_a = cls.calculate_rating_change(expected_a, actual_a)
        rating_change_b = cls.calculate_rating_change(expected_b, actual_b)

        for player in team_a:
            player.elo_rating += rating_change_a
            player.elo_rating = max(1.0, min(player.elo_rating, 7.0))
        for player in team_b:
            player.elo_rating += rating_change_b
            player.elo_rating = max(1.0, min(player.elo_rating, 7.0))

    @classmethod
    def calculate_rating_change(cls, expected_score: float, actual_score: float) -> float:
        """
        Calculates the change in a player's ELO rating.
        
        Args:
            expected_score: The expected score from calculate_expected_score.
            actual_score: The actual outcome of the game (1 for a win, 0.5 for a draw, 0 for a loss).
            
        Returns:
            The amount the player's ELO rating should change.
        """
        return cls.K_FACTOR * (actual_score - expected_score)

# This is a placeholder for the full implementation that will be built up
# through the subtasks.
elo_rating_service = EloRatingService() 