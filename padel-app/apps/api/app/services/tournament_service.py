from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional, Tuple
import math
import random
from datetime import datetime, timedelta

from app.models.tournament import (
    Tournament, TournamentTeam, TournamentMatch, TournamentCategoryConfig,
    TournamentType, MatchStatus, TournamentStatus
)
from app.crud.tournament_crud import tournament_crud
from app.schemas.tournament_schemas import TournamentBracket, BracketNode

class TournamentService:
    
    def generate_bracket(self, db: Session, tournament_id: int, category_config_id: int) -> Optional[TournamentBracket]:
        """Generate tournament bracket based on tournament type and registered teams"""
        tournament = tournament_crud.get_tournament(db, tournament_id)
        if not tournament:
            return None

        category_config = db.query(TournamentCategoryConfig).filter(
            TournamentCategoryConfig.id == category_config_id
        ).first()
        if not category_config:
            return None

        teams = tournament_crud.get_tournament_teams(db, tournament_id, category_config.category)
        if not teams:
            return None

        # Seed teams by ELO rating (highest first)
        teams = sorted(teams, key=lambda t: t.average_elo, reverse=True)
        for i, team in enumerate(teams):
            team.seed = i + 1

        db.commit()

        if tournament.tournament_type == TournamentType.SINGLE_ELIMINATION:
            return self._generate_single_elimination_bracket(db, tournament, category_config, teams)
        elif tournament.tournament_type == TournamentType.DOUBLE_ELIMINATION:
            return self._generate_double_elimination_bracket(db, tournament, category_config, teams)
        elif tournament.tournament_type in [TournamentType.AMERICANO, TournamentType.FIXED_AMERICANO]:
            return self._generate_americano_bracket(db, tournament, category_config, teams)
        
        return None

    def _generate_single_elimination_bracket(self, db: Session, tournament: Tournament, 
                                           category_config: TournamentCategoryConfig, 
                                           teams: List[TournamentTeam]) -> TournamentBracket:
        """Generate single elimination bracket"""
        num_teams = len(teams)
        # Find next power of 2
        bracket_size = 2 ** math.ceil(math.log2(num_teams))
        total_rounds = int(math.log2(bracket_size))
        
        rounds = {}
        
        # First round
        first_round_matches = bracket_size // 2
        rounds[1] = []
        
        # Create first round matches with proper seeding
        match_pairs = self._create_seeded_pairs(teams, bracket_size)
        
        for i, (team1, team2) in enumerate(match_pairs):
            match = tournament_crud.create_match(
                db=db,
                tournament_id=tournament.id,
                category_config_id=category_config.id,
                match_data=type('obj', (object,), {
                    'team1_id': team1.id if team1 else None,
                    'team2_id': team2.id if team2 else None,
                    'round_number': 1,
                    'match_number': i + 1,
                    'scheduled_time': None,
                    'court_id': None
                })()
            )
            
            rounds[1].append(BracketNode(
                match_id=match.id,
                team1_id=team1.id if team1 else None,
                team2_id=team2.id if team2 else None,
                team1_name=team1.team.name if team1 else "BYE",
                team2_name=team2.team.name if team2 else "BYE",
                winning_team_id=None,
                round_number=1,
                match_number=i + 1,
                status=MatchStatus.SCHEDULED
            ))

        # Create subsequent rounds (empty matches to be filled as tournament progresses)
        for round_num in range(2, total_rounds + 1):
            matches_in_round = bracket_size // (2 ** round_num)
            rounds[round_num] = []
            
            for match_num in range(matches_in_round):
                match = tournament_crud.create_match(
                    db=db,
                    tournament_id=tournament.id,
                    category_config_id=category_config.id,
                    match_data=type('obj', (object,), {
                        'team1_id': None,
                        'team2_id': None,
                        'round_number': round_num,
                        'match_number': match_num + 1,
                        'scheduled_time': None,
                        'court_id': None
                    })()
                )
                
                rounds[round_num].append(BracketNode(
                    match_id=match.id,
                    team1_id=None,
                    team2_id=None,
                    team1_name="TBD",
                    team2_name="TBD",
                    winning_team_id=None,
                    round_number=round_num,
                    match_number=match_num + 1,
                    status=MatchStatus.SCHEDULED
                ))

        return TournamentBracket(
            tournament_id=tournament.id,
            category=category_config.category,
            tournament_type=tournament.tournament_type,
            rounds=rounds,
            total_rounds=total_rounds
        )

    def _generate_double_elimination_bracket(self, db: Session, tournament: Tournament,
                                           category_config: TournamentCategoryConfig,
                                           teams: List[TournamentTeam]) -> TournamentBracket:
        """Generate double elimination bracket (simplified version)"""
        # For now, implement as single elimination with additional complexity later
        return self._generate_single_elimination_bracket(db, tournament, category_config, teams)

    def _generate_americano_bracket(self, db: Session, tournament: Tournament,
                                  category_config: TournamentCategoryConfig,
                                  teams: List[TournamentTeam]) -> TournamentBracket:
        """Generate Americano format bracket"""
        # Americano format - all teams play against each other
        num_teams = len(teams)
        rounds = {}
        round_num = 1
        
        # Generate round-robin matches
        for i in range(num_teams):
            for j in range(i + 1, num_teams):
                if round_num not in rounds:
                    rounds[round_num] = []
                
                match = tournament_crud.create_match(
                    db=db,
                    tournament_id=tournament.id,
                    category_config_id=category_config.id,
                    match_data=type('obj', (object,), {
                        'team1_id': teams[i].id,
                        'team2_id': teams[j].id,
                        'round_number': round_num,
                        'match_number': len(rounds[round_num]) + 1,
                        'scheduled_time': None,
                        'court_id': None
                    })()
                )
                
                rounds[round_num].append(BracketNode(
                    match_id=match.id,
                    team1_id=teams[i].id,
                    team2_id=teams[j].id,
                    team1_name=teams[i].team.name,
                    team2_name=teams[j].team.name,
                    winning_team_id=None,
                    round_number=round_num,
                    match_number=len(rounds[round_num]),
                    status=MatchStatus.SCHEDULED
                ))
                
                # Move to next round after 4 matches (assuming 4 courts available)
                if len(rounds[round_num]) >= 4:
                    round_num += 1

        return TournamentBracket(
            tournament_id=tournament.id,
            category=category_config.category,
            tournament_type=tournament.tournament_type,
            rounds=rounds,
            total_rounds=round_num
        )

    def _create_seeded_pairs(self, teams: List[TournamentTeam], bracket_size: int) -> List[Tuple[Optional[TournamentTeam], Optional[TournamentTeam]]]:
        """Create seeded pairs for single elimination tournament"""
        # Standard tournament seeding
        seeds = list(range(1, bracket_size + 1))
        pairs = []
        
        # Create the seeding pairs (1 vs bracket_size, 2 vs bracket_size-1, etc.)
        for i in range(bracket_size // 2):
            seed1 = seeds[i]
            seed2 = seeds[bracket_size - 1 - i]
            
            team1 = teams[seed1 - 1] if seed1 <= len(teams) else None
            team2 = teams[seed2 - 1] if seed2 <= len(teams) else None
            
            pairs.append((team1, team2))
        
        return pairs

    def advance_winner(self, db: Session, match_id: int, winning_team_id: int) -> bool:
        """Advance winning team to next round"""
        match = tournament_crud.get_match(db, match_id)
        if not match:
            return False

        # Update current match
        tournament_crud.update_match(db, match_id, type('obj', (object,), {
            'winning_team_id': winning_team_id,
            'status': MatchStatus.COMPLETED
        })())

        # Find next match to advance to
        if match.winner_advances_to_match_id:
            next_match = tournament_crud.get_match(db, match.winner_advances_to_match_id)
            if next_match:
                # Determine if winner goes to team1 or team2 slot
                if not next_match.team1_id:
                    tournament_crud.update_match(db, next_match.id, type('obj', (object,), {
                        'team1_id': winning_team_id
                    })())
                elif not next_match.team2_id:
                    tournament_crud.update_match(db, next_match.id, type('obj', (object,), {
                        'team2_id': winning_team_id
                    })())

        return True

    def schedule_matches(self, db: Session, tournament_id: int, schedule_config: Dict[str, Any]) -> bool:
        """Schedule matches for a tournament"""
        tournament = tournament_crud.get_tournament(db, tournament_id)
        if not tournament:
            return False

        matches = tournament_crud.get_tournament_matches(db, tournament_id)
        available_courts = [booking.court_id for booking in tournament.court_bookings]
        
        # Group matches by round
        matches_by_round = {}
        for match in matches:
            if match.round_number not in matches_by_round:
                matches_by_round[match.round_number] = []
            matches_by_round[match.round_number].append(match)

        current_time = tournament.start_date
        match_duration = timedelta(hours=1, minutes=30)  # 1.5 hours per match
        break_duration = timedelta(minutes=15)  # 15 minutes between matches

        # Schedule each round
        for round_num in sorted(matches_by_round.keys()):
            round_matches = matches_by_round[round_num]
            
            # Schedule matches in parallel on available courts
            court_index = 0
            for i, match in enumerate(round_matches):
                if match.team1_id and match.team2_id:  # Only schedule matches with both teams
                    court_id = available_courts[court_index % len(available_courts)]
                    schedule_time = current_time + timedelta(hours=i // len(available_courts))
                    
                    tournament_crud.update_match(db, match.id, type('obj', (object,), {
                        'scheduled_time': schedule_time,
                        'court_id': court_id
                    })())
                    
                    court_index += 1

            # Move to next round time
            matches_in_parallel = min(len(available_courts), len([m for m in round_matches if m.team1_id and m.team2_id]))
            if matches_in_parallel > 0:
                rounds_needed = math.ceil(len([m for m in round_matches if m.team1_id and m.team2_id]) / matches_in_parallel)
                current_time += match_duration * rounds_needed + break_duration

        return True

    def get_tournament_bracket(self, db: Session, tournament_id: int, category_config_id: int) -> Optional[TournamentBracket]:
        """Get existing tournament bracket"""
        tournament = tournament_crud.get_tournament(db, tournament_id)
        if not tournament:
            return None

        category_config = db.query(TournamentCategoryConfig).filter(
            TournamentCategoryConfig.id == category_config_id
        ).first()
        if not category_config:
            return None

        matches = tournament_crud.get_tournament_matches(db, tournament_id, category_config.category)
        
        # Group matches by round
        rounds = {}
        for match in matches:
            if match.round_number not in rounds:
                rounds[match.round_number] = []
            
            rounds[match.round_number].append(BracketNode(
                match_id=match.id,
                team1_id=match.team1_id,
                team2_id=match.team2_id,
                team1_name=match.team1.team.name if match.team1 else "TBD",
                team2_name=match.team2.team.name if match.team2 else "TBD",
                winning_team_id=match.winning_team_id,
                round_number=match.round_number,
                match_number=match.match_number,
                status=match.status,
                team1_score=match.team1_score,
                team2_score=match.team2_score
            ))

        return TournamentBracket(
            tournament_id=tournament_id,
            category=category_config.category,
            tournament_type=tournament.tournament_type,
            rounds=rounds,
            total_rounds=max(rounds.keys()) if rounds else 0
        )

    def finalize_tournament(self, db: Session, tournament_id: int) -> bool:
        """Finalize tournament and award trophies"""
        tournament = tournament_crud.get_tournament(db, tournament_id)
        if not tournament:
            return False

        # Update tournament status
        tournament_crud.update_tournament(db, tournament_id, type('obj', (object,), {
            'status': TournamentStatus.COMPLETED
        })())

        # Award trophies for each category
        for category_config in tournament.categories:
            matches = tournament_crud.get_tournament_matches(db, tournament_id, category_config.category)
            
            # Find final match (highest round number)
            final_matches = [m for m in matches if m.round_number == max(m.round_number for m in matches)]
            if not final_matches:
                continue
                
            final_match = final_matches[0]
            if final_match.winning_team_id and final_match.status == MatchStatus.COMPLETED:
                winning_team = db.query(TournamentTeam).filter(
                    TournamentTeam.id == final_match.winning_team_id
                ).first()
                
                if winning_team:
                    # Award trophies to winning team players
                    for player in winning_team.team.players:
                        tournament_crud.award_trophy(
                            db=db,
                            tournament_id=tournament_id,
                            category_config_id=category_config.id,
                            user_id=player.id,
                            team_id=winning_team.team_id,
                            position=1,
                            trophy_type="WINNER"
                        )

        return True

tournament_service = TournamentService()