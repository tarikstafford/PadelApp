from typing import List, Tuple
from collections import defaultdict

from sqlalchemy import desc, asc
from sqlalchemy.orm import Session, joinedload

from app.models.game import Game as GameModel, GameStatus
from app.models.game_player import GamePlayer as GamePlayerModel, GamePlayerStatus, GamePlayerTeamSide
from app.models.user import User as UserModel
from app.models.booking import Booking as BookingModel
from app.models.court import Court as CourtModel
from app.schemas.game_history_schemas import (
    GameHistoryQuery,
    GameHistoryEntry,
    GameHistoryPlayer,
    GameHistoryTeam,
    GameHistoryClub,
    GameResultType,
    GameHistoryFilterType,
    GameStatistics,
    EloProgressionPoint,
    PartnerStatistics,
    ProfileGameHistoryResponse,
)
from app.schemas.user_schemas import UserSearchResult


class GameHistoryCRUD:
    """CRUD operations for game history"""

    def get_user_game_history(
        self,
        db: Session,
        user_id: int,
        query: GameHistoryQuery,
    ) -> Tuple[List[GameHistoryEntry], int]:
        """
        Get game history for a user with filtering and pagination.
        
        Returns:
            Tuple of (games list, total count)
        """
        # Base query - get games where user participated
        base_query = (
            db.query(GameModel)
            .join(GamePlayerModel, GameModel.id == GamePlayerModel.game_id)
            .filter(GamePlayerModel.user_id == user_id)
            .filter(GamePlayerModel.status == GamePlayerStatus.ACCEPTED)
        )

        # Apply filters
        if query.completed_only:
            base_query = base_query.filter(GameModel.game_status == GameStatus.COMPLETED)

        if query.start_date:
            base_query = base_query.filter(GameModel.start_time >= query.start_date)

        if query.end_date:
            base_query = base_query.filter(GameModel.end_time <= query.end_date)

        if query.club_id:
            base_query = base_query.filter(GameModel.club_id == query.club_id)

        # Apply partner filter
        if query.partner_id:
            partner_subquery = (
                db.query(GamePlayerModel.game_id)
                .filter(GamePlayerModel.user_id == query.partner_id)
                .filter(GamePlayerModel.status == GamePlayerStatus.ACCEPTED)
                .subquery()
            )
            base_query = base_query.filter(GameModel.id.in_(partner_subquery))

        # Apply opponent filter
        if query.opponent_id:
            # Get user's team side for games, then filter for opponent
            user_team_subquery = (
                db.query(GamePlayerModel.game_id, GamePlayerModel.team_side)
                .filter(GamePlayerModel.user_id == user_id)
                .filter(GamePlayerModel.status == GamePlayerStatus.ACCEPTED)
                .subquery()
            )

            opponent_subquery = (
                db.query(GamePlayerModel.game_id)
                .join(user_team_subquery, GamePlayerModel.game_id == user_team_subquery.c.game_id)
                .filter(GamePlayerModel.user_id == query.opponent_id)
                .filter(GamePlayerModel.status == GamePlayerStatus.ACCEPTED)
                .filter(GamePlayerModel.team_side != user_team_subquery.c.team_side)
                .subquery()
            )
            base_query = base_query.filter(GameModel.id.in_(opponent_subquery))

        # Get total count before pagination
        total_count = base_query.count()

        # Apply pagination and ordering
        games = (
            base_query
            .order_by(desc(GameModel.start_time))
            .offset(query.skip)
            .limit(query.limit)
            .options(
                joinedload(GameModel.booking).joinedload(BookingModel.court).joinedload(CourtModel.club),
                joinedload(GameModel.players).joinedload(GamePlayerModel.user),
                joinedload(GameModel.scores)
            )
            .all()
        )

        # Convert to history entries
        history_entries = []
        for game in games:
            entry = self._convert_game_to_history_entry(game, user_id)

            # Apply result filter
            if query.result_filter and query.result_filter != GameHistoryFilterType.ALL:
                if query.result_filter == GameHistoryFilterType.WINS and entry.result != GameResultType.WIN:
                    continue
                elif query.result_filter == GameHistoryFilterType.LOSSES and entry.result != GameResultType.LOSS:
                    continue
                elif query.result_filter == GameHistoryFilterType.DRAWS and entry.result != GameResultType.DRAW:
                    continue

            history_entries.append(entry)

        return history_entries, total_count

    def get_user_game_statistics(
        self,
        db: Session,
        user_id: int,
        limit_recent: int = 10,
    ) -> GameStatistics:
        """Get comprehensive game statistics for a user"""

        # Get all completed games for the user
        games = (
            db.query(GameModel)
            .join(GamePlayerModel, GameModel.id == GamePlayerModel.game_id)
            .filter(GamePlayerModel.user_id == user_id)
            .filter(GamePlayerModel.status == GamePlayerStatus.ACCEPTED)
            .filter(GameModel.game_status == GameStatus.COMPLETED)
            .options(
                joinedload(GameModel.players).joinedload(GamePlayerModel.user),
                joinedload(GameModel.scores)
            )
            .order_by(desc(GameModel.start_time))
            .all()
        )

        # Calculate basic statistics
        total_games = len(games)
        wins = 0
        losses = 0
        draws = 0

        # Track ELO progression
        elo_ratings = []
        recent_results = []
        partner_counts = defaultdict(int)

        # Get current user
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        current_elo = user.elo_rating if user else 1.0

        # Process each game
        for game in games[:limit_recent]:
            entry = self._convert_game_to_history_entry(game, user_id)

            # Count results
            if entry.result == GameResultType.WIN:
                wins += 1
            elif entry.result == GameResultType.LOSS:
                losses += 1
            else:
                draws += 1

            # Track recent form
            recent_results.append(entry.result)

            # Track ELO progression
            if entry.elo_after is not None:
                elo_ratings.append(entry.elo_after)

            # Count partners
            for partner in entry.partners:
                partner_counts[partner.id] += 1

        # Calculate win rate
        win_rate = (wins / total_games) if total_games > 0 else 0.0

        # Calculate ELO statistics
        highest_elo = max(elo_ratings) if elo_ratings else current_elo
        lowest_elo = min(elo_ratings) if elo_ratings else current_elo
        elo_change_total = (current_elo - elo_ratings[-1]) if elo_ratings else 0.0

        # Get favorite partners
        favorite_partners = []
        if partner_counts:
            # Get top 3 partners
            top_partners = sorted(partner_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            partner_ids = [partner_id for partner_id, _ in top_partners]

            partners = (
                db.query(UserModel)
                .filter(UserModel.id.in_(partner_ids))
                .all()
            )

            favorite_partners = [
                UserSearchResult(
                    id=partner.id,
                    full_name=partner.full_name,
                    profile_picture_url=partner.profile_picture_url,
                )
                for partner in partners
            ]

        return GameStatistics(
            total_games=total_games,
            wins=wins,
            losses=losses,
            draws=draws,
            win_rate=win_rate,
            current_elo=current_elo,
            highest_elo=highest_elo,
            lowest_elo=lowest_elo,
            elo_change_total=elo_change_total,
            favorite_partners=favorite_partners,
            recent_form=recent_results,
        )

    def get_user_elo_progression(
        self,
        db: Session,
        user_id: int,
        limit: int = 50,
    ) -> List[EloProgressionPoint]:
        """Get ELO progression over time for a user"""

        # Get completed games ordered by date
        games = (
            db.query(GameModel)
            .join(GamePlayerModel, GameModel.id == GamePlayerModel.game_id)
            .filter(GamePlayerModel.user_id == user_id)
            .filter(GamePlayerModel.status == GamePlayerStatus.ACCEPTED)
            .filter(GameModel.game_status == GameStatus.COMPLETED)
            .options(
                joinedload(GameModel.players).joinedload(GamePlayerModel.user)
            )
            .order_by(asc(GameModel.start_time))
            .limit(limit)
            .all()
        )

        progression = []
        for game in games:
            entry = self._convert_game_to_history_entry(game, user_id)

            # Calculate opponent average ELO
            opponent_elos = [opponent.elo_rating for opponent in entry.opponents]
            opponent_avg_elo = sum(opponent_elos) / len(opponent_elos) if opponent_elos else 1.0

            if entry.elo_after is not None and entry.elo_change is not None:
                progression.append(
                    EloProgressionPoint(
                        game_id=game.id,
                        date=game.start_time,
                        elo_rating=entry.elo_after,
                        elo_change=entry.elo_change,
                        opponent_average_elo=opponent_avg_elo,
                        result=entry.result,
                    )
                )

        return progression

    def get_partner_statistics(
        self,
        db: Session,
        user_id: int,
        limit: int = 10,
    ) -> List[PartnerStatistics]:
        """Get statistics with different partners"""

        # Get all games where user participated
        games = (
            db.query(GameModel)
            .join(GamePlayerModel, GameModel.id == GamePlayerModel.game_id)
            .filter(GamePlayerModel.user_id == user_id)
            .filter(GamePlayerModel.status == GamePlayerStatus.ACCEPTED)
            .filter(GameModel.game_status == GameStatus.COMPLETED)
            .options(
                joinedload(GameModel.players).joinedload(GamePlayerModel.user)
            )
            .all()
        )

        # Track partner statistics
        partner_stats = defaultdict(lambda: {"games": 0, "wins": 0, "losses": 0, "draws": 0})

        for game in games:
            entry = self._convert_game_to_history_entry(game, user_id)

            for partner in entry.partners:
                partner_stats[partner.id]["games"] += 1
                if entry.result == GameResultType.WIN:
                    partner_stats[partner.id]["wins"] += 1
                elif entry.result == GameResultType.LOSS:
                    partner_stats[partner.id]["losses"] += 1
                else:
                    partner_stats[partner.id]["draws"] += 1

        # Convert to response format
        if not partner_stats:
            return []

        # Get partner user objects
        partner_ids = list(partner_stats.keys())
        partners = (
            db.query(UserModel)
            .filter(UserModel.id.in_(partner_ids))
            .all()
        )

        partner_objects = {partner.id: partner for partner in partners}

        # Create statistics objects
        statistics = []
        for partner_id, stats in partner_stats.items():
            if partner_id in partner_objects:
                partner = partner_objects[partner_id]
                win_rate = stats["wins"] / stats["games"] if stats["games"] > 0 else 0.0

                statistics.append(
                    PartnerStatistics(
                        partner=UserSearchResult(
                            id=partner.id,
                            full_name=partner.full_name,
                            profile_picture_url=partner.profile_picture_url,
                        ),
                        games_together=stats["games"],
                        wins_together=stats["wins"],
                        losses_together=stats["losses"],
                        draws_together=stats["draws"],
                        win_rate_together=win_rate,
                    )
                )

        # Sort by games together and return top results
        statistics.sort(key=lambda x: x.games_together, reverse=True)
        return statistics[:limit]

    def get_public_game_history(
        self,
        db: Session,
        user_id: int,
        limit: int = 5,
    ) -> ProfileGameHistoryResponse:
        """Get public game history for user profiles"""

        # Get user to check privacy settings
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            return ProfileGameHistoryResponse(
                total_games=0,
                wins=0,
                losses=0,
                win_rate=0.0,
                current_elo=1.0,
                is_history_public=False,
                is_statistics_public=False,
            )

        # Get basic statistics (always available)
        stats = self.get_user_game_statistics(db, user_id)

        # Check privacy settings (assuming they exist on user model)
        is_history_public = getattr(user, 'is_game_history_public', True)
        is_statistics_public = getattr(user, 'is_game_statistics_public', True)

        response = ProfileGameHistoryResponse(
            total_games=stats.total_games,
            wins=stats.wins,
            losses=stats.losses,
            win_rate=stats.win_rate,
            current_elo=stats.current_elo,
            is_history_public=is_history_public,
            is_statistics_public=is_statistics_public,
        )

        # Add detailed information if privacy allows
        if is_history_public:
            query = GameHistoryQuery(skip=0, limit=limit)
            recent_games, _ = self.get_user_game_history(db, user_id, query)
            response.recent_games = recent_games

        if is_statistics_public:
            response.favorite_partners = stats.favorite_partners

        return response

    def _convert_game_to_history_entry(
        self,
        game: GameModel,
        user_id: int,
    ) -> GameHistoryEntry:
        """Convert a game model to a history entry from the user's perspective"""

        # Find user's team side
        user_team_side = None
        user_player = None
        for player in game.players:
            if player.user_id == user_id and player.status == GamePlayerStatus.ACCEPTED:
                user_team_side = player.team_side
                user_player = player
                break

        if not user_team_side:
            # Default to TEAM_1 if not found
            user_team_side = GamePlayerTeamSide.TEAM_1

        # Separate players by team
        team1_players = []
        team2_players = []

        for player in game.players:
            if player.status == GamePlayerStatus.ACCEPTED:
                history_player = GameHistoryPlayer(
                    id=player.user.id,
                    full_name=player.user.full_name,
                    profile_picture_url=player.user.profile_picture_url,
                    elo_rating=player.user.elo_rating,
                    position=player.position.value if player.position else None,
                    team_side=player.team_side.value if player.team_side else None,
                )

                if player.team_side == GamePlayerTeamSide.TEAM_1:
                    team1_players.append(history_player)
                else:
                    team2_players.append(history_player)

        # Determine if teams won
        team1_won = game.winning_team_id == game.team1_id if game.winning_team_id else False
        team2_won = game.winning_team_id == game.team2_id if game.winning_team_id else False

        # Create team objects
        team1 = GameHistoryTeam(players=team1_players, is_winning_team=team1_won)
        team2 = GameHistoryTeam(players=team2_players, is_winning_team=team2_won)

        # Determine result from user's perspective
        result = GameResultType.DRAW
        if game.winning_team_id:
            if (user_team_side == GamePlayerTeamSide.TEAM_1 and team1_won) or \
               (user_team_side == GamePlayerTeamSide.TEAM_2 and team2_won):
                result = GameResultType.WIN
            else:
                result = GameResultType.LOSS

        # Get partners and opponents
        partners = []
        opponents = []

        for player in game.players:
            if player.status == GamePlayerStatus.ACCEPTED and player.user_id != user_id:
                history_player = GameHistoryPlayer(
                    id=player.user.id,
                    full_name=player.user.full_name,
                    profile_picture_url=player.user.profile_picture_url,
                    elo_rating=player.user.elo_rating,
                    position=player.position.value if player.position else None,
                    team_side=player.team_side.value if player.team_side else None,
                )

                if player.team_side == user_team_side:
                    partners.append(history_player)
                else:
                    opponents.append(history_player)

        # Get game score
        score = None
        if game.scores:
            # Get the most recent confirmed score
            confirmed_scores = [s for s in game.scores if s.is_confirmed]
            if confirmed_scores:
                score = confirmed_scores[-1].score

        # Create club info
        club = GameHistoryClub(
            id=game.club_id,
            name=game.booking.court.club.name,
            city=getattr(game.booking.court.club, 'city', None),
        )

        # TODO: Calculate ELO changes (this would require storing historical ELO data)
        # For now, we'll leave these as None
        elo_change = None
        elo_before = None
        elo_after = None

        return GameHistoryEntry(
            id=game.id,
            game_id=game.id,
            start_time=game.start_time,
            end_time=game.end_time,
            club=club,
            team1=team1,
            team2=team2,
            result=result,
            user_team_side=user_team_side.value,
            score=score,
            elo_change=elo_change,
            elo_before=elo_before,
            elo_after=elo_after,
            partners=partners,
            opponents=opponents,
        )


# Create instance
game_history_crud = GameHistoryCRUD()
