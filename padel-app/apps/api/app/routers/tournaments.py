from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.club_admin import ClubAdmin
from app.models.tournament import TournamentStatus, TournamentCategory
from app.crud.tournament_crud import tournament_crud
from app.services.tournament_service import tournament_service
from app.services.elo_rating_service import elo_rating_service
from app.schemas.tournament_schemas import (
    TournamentCreate, TournamentUpdate, TournamentResponse, TournamentListResponse,
    TournamentTeamCreate, TournamentTeamResponse, TournamentMatchUpdate, TournamentMatchResponse,
    TournamentBracket, TeamEligibilityCheck, TournamentStats, TournamentDashboard
)

router = APIRouter(prefix="/tournaments", tags=["tournaments"])

def get_club_admin_user(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Ensure current user is a club admin"""
    club_admin = db.query(ClubAdmin).filter(ClubAdmin.user_id == current_user.id).first()
    if not club_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only club administrators can perform this action"
        )
    return current_user, club_admin

@router.post("/", response_model=TournamentResponse)
async def create_tournament(
    tournament_data: TournamentCreate,
    db: Session = Depends(get_db),
    user_and_admin: tuple = Depends(get_club_admin_user)
):
    """Create a new tournament (Admin only)"""
    current_user, club_admin = user_and_admin
    
    try:
        tournament = tournament_crud.create_tournament(
            db=db, 
            tournament_data=tournament_data, 
            club_id=club_admin.club_id
        )
        
        # Convert to response format
        return TournamentResponse(
            id=tournament.id,
            club_id=tournament.club_id,
            name=tournament.name,
            description=tournament.description,
            tournament_type=tournament.tournament_type,
            start_date=tournament.start_date,
            end_date=tournament.end_date,
            registration_deadline=tournament.registration_deadline,
            status=tournament.status,
            max_participants=tournament.max_participants,
            entry_fee=tournament.entry_fee,
            created_at=tournament.created_at,
            updated_at=tournament.updated_at,
            categories=[],
            total_registered_teams=0
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create tournament: {str(e)}"
        )

@router.get("/club", response_model=List[TournamentListResponse])
async def get_club_tournaments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    user_and_admin: tuple = Depends(get_club_admin_user)
):
    """Get tournaments for the admin's club"""
    current_user, club_admin = user_and_admin
    
    tournaments = tournament_crud.get_tournaments_by_club(
        db=db, 
        club_id=club_admin.club_id, 
        skip=skip, 
        limit=limit
    )
    
    return [
        TournamentListResponse(
            id=t.id,
            name=t.name,
            tournament_type=t.tournament_type,
            start_date=t.start_date,
            end_date=t.end_date,
            status=t.status,
            total_registered_teams=len(t.teams),
            max_participants=t.max_participants
        ) for t in tournaments
    ]

@router.get("/{tournament_id}", response_model=TournamentResponse)
async def get_tournament(
    tournament_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get tournament details"""
    tournament = tournament_crud.get_tournament(db=db, tournament_id=tournament_id)
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found"
        )
    
    return TournamentResponse(
        id=tournament.id,
        club_id=tournament.club_id,
        name=tournament.name,
        description=tournament.description,
        tournament_type=tournament.tournament_type,
        start_date=tournament.start_date,
        end_date=tournament.end_date,
        registration_deadline=tournament.registration_deadline,
        status=tournament.status,
        max_participants=tournament.max_participants,
        entry_fee=tournament.entry_fee,
        created_at=tournament.created_at,
        updated_at=tournament.updated_at,
        categories=[],
        total_registered_teams=len(tournament.teams)
    )

@router.put("/{tournament_id}", response_model=TournamentResponse)
async def update_tournament(
    tournament_id: int,
    tournament_data: TournamentUpdate,
    db: Session = Depends(get_db),
    user_and_admin: tuple = Depends(get_club_admin_user)
):
    """Update tournament (Admin only)"""
    current_user, club_admin = user_and_admin
    
    # Verify tournament belongs to admin's club
    tournament = tournament_crud.get_tournament(db=db, tournament_id=tournament_id)
    if not tournament or tournament.club_id != club_admin.club_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found"
        )
    
    updated_tournament = tournament_crud.update_tournament(
        db=db, 
        tournament_id=tournament_id, 
        tournament_data=tournament_data
    )
    
    if not updated_tournament:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update tournament"
        )
    
    return TournamentResponse(
        id=updated_tournament.id,
        club_id=updated_tournament.club_id,
        name=updated_tournament.name,
        description=updated_tournament.description,
        tournament_type=updated_tournament.tournament_type,
        start_date=updated_tournament.start_date,
        end_date=updated_tournament.end_date,
        registration_deadline=updated_tournament.registration_deadline,
        status=updated_tournament.status,
        max_participants=updated_tournament.max_participants,
        entry_fee=updated_tournament.entry_fee,
        created_at=updated_tournament.created_at,
        updated_at=updated_tournament.updated_at,
        categories=[],
        total_registered_teams=len(updated_tournament.teams)
    )

@router.delete("/{tournament_id}")
async def delete_tournament(
    tournament_id: int,
    db: Session = Depends(get_db),
    user_and_admin: tuple = Depends(get_club_admin_user)
):
    """Delete tournament (Admin only)"""
    current_user, club_admin = user_and_admin
    
    # Verify tournament belongs to admin's club
    tournament = tournament_crud.get_tournament(db=db, tournament_id=tournament_id)
    if not tournament or tournament.club_id != club_admin.club_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found"
        )
    
    success = tournament_crud.delete_tournament(db=db, tournament_id=tournament_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete tournament"
        )
    
    return {"message": "Tournament deleted successfully"}

@router.post("/{tournament_id}/register", response_model=TournamentTeamResponse)
async def register_team(
    tournament_id: int,
    team_data: TournamentTeamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Register team for tournament"""
    tournament_team = tournament_crud.register_team(
        db=db, 
        tournament_id=tournament_id, 
        team_data=team_data
    )
    
    if not tournament_team:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to register team. Check eligibility and availability."
        )
    
    return TournamentTeamResponse(
        id=tournament_team.id,
        team_id=tournament_team.team_id,
        team_name=tournament_team.team.name,
        category=tournament_team.category_config.category,
        seed=tournament_team.seed,
        average_elo=tournament_team.average_elo,
        registration_date=tournament_team.registration_date,
        is_active=tournament_team.is_active,
        players=[]
    )

@router.delete("/{tournament_id}/teams/{team_id}")
async def unregister_team(
    tournament_id: int,
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Unregister team from tournament"""
    success = tournament_crud.unregister_team(
        db=db, 
        tournament_id=tournament_id, 
        team_id=team_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team registration not found"
        )
    
    return {"message": "Team unregistered successfully"}

@router.get("/{tournament_id}/teams", response_model=List[TournamentTeamResponse])
async def get_tournament_teams(
    tournament_id: int,
    category: Optional[TournamentCategory] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get registered teams for tournament"""
    teams = tournament_crud.get_tournament_teams(
        db=db, 
        tournament_id=tournament_id, 
        category=category
    )
    
    return [
        TournamentTeamResponse(
            id=team.id,
            team_id=team.team_id,
            team_name=team.team.name,
            category=team.category_config.category,
            seed=team.seed,
            average_elo=team.average_elo,
            registration_date=team.registration_date,
            is_active=team.is_active,
            players=[
                {"id": p.id, "name": p.full_name, "elo": p.elo_rating} 
                for p in team.team.players
            ]
        ) for team in teams
    ]

@router.post("/{tournament_id}/generate-bracket")
async def generate_tournament_bracket(
    tournament_id: int,
    category_config_id: int,
    db: Session = Depends(get_db),
    user_and_admin: tuple = Depends(get_club_admin_user)
):
    """Generate tournament bracket (Admin only)"""
    current_user, club_admin = user_and_admin
    
    # Verify tournament belongs to admin's club
    tournament = tournament_crud.get_tournament(db=db, tournament_id=tournament_id)
    if not tournament or tournament.club_id != club_admin.club_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found"
        )
    
    bracket = tournament_service.generate_bracket(
        db=db, 
        tournament_id=tournament_id, 
        category_config_id=category_config_id
    )
    
    if not bracket:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to generate bracket"
        )
    
    return bracket

@router.get("/{tournament_id}/bracket", response_model=TournamentBracket)
async def get_tournament_bracket(
    tournament_id: int,
    category_config_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get tournament bracket"""
    bracket = tournament_service.get_tournament_bracket(
        db=db, 
        tournament_id=tournament_id, 
        category_config_id=category_config_id
    )
    
    if not bracket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bracket not found"
        )
    
    return bracket

@router.get("/{tournament_id}/matches", response_model=List[TournamentMatchResponse])
async def get_tournament_matches(
    tournament_id: int,
    category: Optional[TournamentCategory] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get tournament matches"""
    matches = tournament_crud.get_tournament_matches(
        db=db, 
        tournament_id=tournament_id, 
        category=category
    )
    
    return [
        TournamentMatchResponse(
            id=match.id,
            tournament_id=match.tournament_id,
            category=match.category_config.category,
            team1_id=match.team1_id,
            team2_id=match.team2_id,
            team1_name=match.team1.team.name if match.team1 else None,
            team2_name=match.team2.team.name if match.team2 else None,
            round_number=match.round_number,
            match_number=match.match_number,
            scheduled_time=match.scheduled_time,
            court_id=match.court_id,
            court_name=match.court.name if match.court else None,
            status=match.status,
            winning_team_id=match.winning_team_id,
            team1_score=match.team1_score,
            team2_score=match.team2_score,
            winner_advances_to_match_id=match.winner_advances_to_match_id,
            loser_advances_to_match_id=match.loser_advances_to_match_id
        ) for match in matches
    ]

@router.put("/matches/{match_id}", response_model=TournamentMatchResponse)
async def update_match_result(
    match_id: int,
    match_data: TournamentMatchUpdate,
    db: Session = Depends(get_db),
    user_and_admin: tuple = Depends(get_club_admin_user)
):
    """Update match result (Admin only)"""
    current_user, club_admin = user_and_admin
    
    # Verify match belongs to admin's club tournament
    match = tournament_crud.get_match(db=db, match_id=match_id)
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )
    
    tournament = tournament_crud.get_tournament(db=db, tournament_id=match.tournament_id)
    if not tournament or tournament.club_id != club_admin.club_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    updated_match = tournament_crud.update_match(
        db=db, 
        match_id=match_id, 
        match_data=match_data
    )
    
    if not updated_match:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update match"
        )
    
    # If match is completed, advance winner and update ELO ratings
    if match_data.winning_team_id and match_data.status == "COMPLETED":
        tournament_service.advance_winner(
            db=db, 
            match_id=match_id, 
            winning_team_id=match_data.winning_team_id
        )
        
        # Update ELO ratings for tournament match
        elo_rating_service.update_tournament_match_ratings(updated_match, db)
    
    return TournamentMatchResponse(
        id=updated_match.id,
        tournament_id=updated_match.tournament_id,
        category=updated_match.category_config.category,
        team1_id=updated_match.team1_id,
        team2_id=updated_match.team2_id,
        team1_name=updated_match.team1.team.name if updated_match.team1 else None,
        team2_name=updated_match.team2.team.name if updated_match.team2 else None,
        round_number=updated_match.round_number,
        match_number=updated_match.match_number,
        scheduled_time=updated_match.scheduled_time,
        court_id=updated_match.court_id,
        court_name=updated_match.court.name if updated_match.court else None,
        status=updated_match.status,
        winning_team_id=updated_match.winning_team_id,
        team1_score=updated_match.team1_score,
        team2_score=updated_match.team2_score,
        winner_advances_to_match_id=updated_match.winner_advances_to_match_id,
        loser_advances_to_match_id=updated_match.loser_advances_to_match_id
    )

@router.get("/{tournament_id}/eligibility/{team_id}")
async def check_team_eligibility(
    tournament_id: int,
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Check team eligibility for tournament"""
    eligibility = tournament_crud.check_team_eligibility(
        db=db, 
        tournament_id=tournament_id, 
        team_id=team_id
    )
    
    return eligibility

@router.get("/{tournament_id}/stats", response_model=TournamentStats)
async def get_tournament_stats(
    tournament_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get tournament statistics"""
    stats = tournament_crud.get_tournament_stats(db=db, tournament_id=tournament_id)
    
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found"
        )
    
    return TournamentStats(**stats)

@router.post("/{tournament_id}/finalize")
async def finalize_tournament(
    tournament_id: int,
    db: Session = Depends(get_db),
    user_and_admin: tuple = Depends(get_club_admin_user)
):
    """Finalize tournament and award trophies (Admin only)"""
    current_user, club_admin = user_and_admin
    
    # Verify tournament belongs to admin's club
    tournament = tournament_crud.get_tournament(db=db, tournament_id=tournament_id)
    if not tournament or tournament.club_id != club_admin.club_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found"
        )
    
    success = tournament_service.finalize_tournament(db=db, tournament_id=tournament_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to finalize tournament"
        )
    
    return {"message": "Tournament finalized successfully"}

@router.get("/", response_model=List[TournamentListResponse])
async def get_public_tournaments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[TournamentStatus] = Query(None),
    db: Session = Depends(get_db)
):
    """Get public tournaments (no auth required)"""
    if status:
        tournaments = tournament_crud.get_tournaments_by_status(
            db=db, 
            status=status, 
            skip=skip, 
            limit=limit
        )
    else:
        # Get all tournaments with registration open
        tournaments = tournament_crud.get_tournaments_by_status(
            db=db, 
            status=TournamentStatus.REGISTRATION_OPEN, 
            skip=skip, 
            limit=limit
        )
    
    return [
        TournamentListResponse(
            id=t.id,
            name=t.name,
            tournament_type=t.tournament_type,
            start_date=t.start_date,
            end_date=t.end_date,
            status=t.status,
            total_registered_teams=len(t.teams),
            max_participants=t.max_participants
        ) for t in tournaments
    ]