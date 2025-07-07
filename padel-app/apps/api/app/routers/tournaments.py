import contextlib
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.security import get_current_active_user
from app.crud.tournament_crud import tournament_crud
from app.database import get_db
from app.models.club_admin import ClubAdmin
from app.models.tournament import TournamentCategory, TournamentStatus
from app.models.user import User
from app.schemas.tournament_schemas import (
    CourtAvailabilityRequest,
    CourtAvailabilityResponse,
    TournamentBracket,
    TournamentCourtBookingBulkCreate,
    TournamentCourtBookingBulkResponse,
    TournamentCreate,
    TournamentListResponse,
    TournamentMatchResponse,
    TournamentMatchUpdate,
    TournamentParticipantResponse,
    TournamentRegistrationRequest,
    TournamentResponse,
    TournamentScheduleCalculation,
    TournamentScheduleCalculationResponse,
    TournamentScheduleRequest,
    TournamentScheduleResponse,
    TournamentScheduleSummary,
    TournamentStats,
    TournamentTeamCreate,
    TournamentTeamResponse,
    TournamentUpdate,
)
from app.services.court_booking_service import court_booking_service
from app.services.elo_rating_service import elo_rating_service
from app.services.tournament_schedule_service import tournament_schedule_service
from app.services.tournament_service import tournament_service

router = APIRouter(prefix="/tournaments", tags=["tournaments"])


# Add CORS preflight handler
@router.options("/{path:path}")
async def options_handler():
    """Handle CORS preflight requests"""
    return {"message": "OK"}


def get_club_admin_user(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    """Ensure current user is a club admin"""
    club_admin = (
        db.query(ClubAdmin).filter(ClubAdmin.user_id == current_user.id).first()
    )
    if not club_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only club administrators can perform this action",
        )
    return current_user, club_admin


@router.post("", response_model=TournamentResponse)
async def create_tournament(
    tournament_data: TournamentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new tournament (Admin only)"""
    # Check if user owns a club or is a club admin
    club_id = None
    if current_user.owned_club:
        club_id = current_user.owned_club.id
    else:
        # Check if user is a club admin
        club_admin = (
            db.query(ClubAdmin).filter(ClubAdmin.user_id == current_user.id).first()
        )
        if club_admin:
            club_id = club_admin.club_id

    if not club_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only club administrators can perform this action",
        )

    try:
        tournament = tournament_crud.create_tournament(
            db=db, tournament_data=tournament_data, club_id=club_id
        )

        # Convert to response format
        from app.models.tournament import TournamentType

        is_americano = tournament.tournament_type in [
            TournamentType.AMERICANO,
            TournamentType.FIXED_AMERICANO,
        ]

        # Build category data
        categories_data = []
        for category in tournament.categories:
            categories_data.append(
                TournamentCategoryResponse(
                    id=category.id,
                    category=category.category,
                    max_participants=category.max_participants,
                    min_elo=category.min_elo,
                    max_elo=category.max_elo,
                    current_participants=0,  # New tournament has no registrations yet
                    current_teams=0,
                    current_individuals=0,
                )
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
            categories=categories_data,
            total_registered_teams=0,
            total_registered_participants=0,
            requires_teams=not is_americano,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create tournament: {e!s}",
        )


@router.get("/club", response_model=list[TournamentListResponse])
async def get_club_tournaments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get tournaments for the admin's club"""
    # Check if user owns a club or is a club admin
    club_id = None
    if current_user.owned_club:
        club_id = current_user.owned_club.id
    else:
        # Check if user is a club admin
        club_admin = (
            db.query(ClubAdmin).filter(ClubAdmin.user_id == current_user.id).first()
        )
        if club_admin:
            club_id = club_admin.club_id

    if not club_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only club administrators can perform this action",
        )

    tournaments = tournament_crud.get_tournaments_by_club(
        db=db, club_id=club_id, skip=skip, limit=limit
    )

    # Ensure we always return an empty list if no tournaments found
    if not tournaments:
        return []

    return [
        TournamentListResponse(
            id=t.id,
            name=t.name,
            tournament_type=t.tournament_type,
            start_date=t.start_date,
            end_date=t.end_date,
            status=t.status,
            total_registered_teams=len(t.teams),
            max_participants=t.max_participants,
            entry_fee=t.entry_fee,
            club_name=t.club.name if t.club else None,
        )
        for t in tournaments
    ]


@router.get("/", response_model=list[TournamentListResponse])
async def get_public_tournaments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[TournamentStatus] = Query(None),
    db: Session = Depends(get_db),
):
    """Get public tournaments (no auth required)"""
    if status:
        tournaments = tournament_crud.get_tournaments_by_status(
            db=db, status=status, skip=skip, limit=limit
        )
    else:
        # Get all tournaments
        tournaments = tournament_crud.get_tournaments(db=db, skip=skip, limit=limit)

    return [
        TournamentListResponse(
            id=t.id,
            name=t.name,
            tournament_type=t.tournament_type,
            start_date=t.start_date,
            end_date=t.end_date,
            status=t.status,
            total_registered_teams=len(t.teams),
            max_participants=t.max_participants,
            entry_fee=t.entry_fee,
            club_name=t.club.name if t.club else None,
        )
        for t in tournaments
    ]


@router.get("/{tournament_id}", response_model=TournamentResponse)
async def get_tournament(tournament_id: int, db: Session = Depends(get_db)):
    """Get tournament details (public endpoint)"""
    try:
        tournament = tournament_crud.get_tournament(db=db, tournament_id=tournament_id)
        if not tournament:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tournament not found"
            )

        # Create response with actual data
        from app.models.tournament import TournamentType

        is_americano = tournament.tournament_type in [
            TournamentType.AMERICANO,
            TournamentType.FIXED_AMERICANO,
        ]

        # Calculate category data
        categories_data = []
        for category in tournament.categories:
            team_count = len(
                [t for t in tournament.teams if t.category_config_id == category.id]
            )
            participant_count = len(
                [
                    p
                    for p in tournament.participants
                    if p.category_config_id == category.id
                ]
            )

            categories_data.append(
                TournamentCategoryResponse(
                    id=category.id,
                    category=category.category,
                    max_participants=category.max_participants,
                    min_elo=category.min_elo,
                    max_elo=category.max_elo,
                    current_participants=participant_count
                    if is_americano
                    else team_count,
                    current_teams=team_count,
                    current_individuals=participant_count,
                )
            )

        return TournamentResponse(
            id=tournament.id,
            club_id=tournament.club_id,
            name=tournament.name or "",
            description=tournament.description or "",
            tournament_type=tournament.tournament_type,
            start_date=tournament.start_date,
            end_date=tournament.end_date,
            registration_deadline=tournament.registration_deadline,
            status=tournament.status,
            max_participants=tournament.max_participants or 0,
            entry_fee=tournament.entry_fee or 0.0,
            created_at=tournament.created_at,
            updated_at=tournament.updated_at,
            categories=categories_data,
            total_registered_teams=len(tournament.teams) if tournament.teams else 0,
            total_registered_participants=len(tournament.participants)
            if tournament.participants
            else 0,
            requires_teams=not is_americano,
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception:
        # Log error and return generic 500
        # TODO: Replace with proper logging
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.put("/{tournament_id}", response_model=TournamentResponse)
async def update_tournament(
    tournament_id: int,
    tournament_data: TournamentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update tournament (Admin only)"""
    # Check if user owns a club or is a club admin
    club_id = None
    if current_user.owned_club:
        club_id = current_user.owned_club.id
    else:
        # Check if user is a club admin
        club_admin = (
            db.query(ClubAdmin).filter(ClubAdmin.user_id == current_user.id).first()
        )
        if club_admin:
            club_id = club_admin.club_id

    if not club_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only club administrators can perform this action",
        )

    # Verify tournament belongs to admin's club
    tournament = tournament_crud.get_tournament(db=db, tournament_id=tournament_id)
    if not tournament or tournament.club_id != club_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tournament not found"
        )

    updated_tournament = tournament_crud.update_tournament(
        db=db, tournament_id=tournament_id, tournament_data=tournament_data
    )

    if not updated_tournament:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update tournament",
        )

    # Safe calculation of registered teams
    with contextlib.suppress(AttributeError, TypeError):
        len(updated_tournament.teams) if updated_tournament.teams else 0

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
        categories=[category.category for category in updated_tournament.categories],
        total_registered_teams=(
            len(updated_tournament.teams) if updated_tournament.teams else 0
        ),
    )


@router.delete("/{tournament_id}")
async def delete_tournament(
    tournament_id: int,
    db: Session = Depends(get_db),
    user_and_admin: tuple = Depends(get_club_admin_user),
):
    """Delete tournament (Admin only)"""
    current_user, club_admin = user_and_admin

    # Verify tournament belongs to admin's club
    tournament = tournament_crud.get_tournament(db=db, tournament_id=tournament_id)
    if not tournament or tournament.club_id != club_admin.club_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tournament not found"
        )

    success = tournament_crud.delete_tournament(db=db, tournament_id=tournament_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete tournament",
        )

    return {"message": "Tournament deleted successfully"}


@router.post("/{tournament_id}/register")
async def register_for_tournament(
    tournament_id: int,
    registration_data: TournamentRegistrationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Unified registration endpoint that handles both team and individual registrations"""
    # Get tournament to check type
    tournament = tournament_crud.get_tournament(db=db, tournament_id=tournament_id)
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tournament not found"
        )

    # Check if tournament requires teams or individuals
    from app.models.tournament import TournamentType

    is_americano = tournament.tournament_type in [
        TournamentType.AMERICANO,
        TournamentType.FIXED_AMERICANO,
    ]

    if is_americano:
        # Individual registration for Americano tournaments
        eligibility = tournament_crud.check_participant_eligibility(
            db=db, tournament_id=tournament_id, user_id=current_user.id
        )

        if not eligibility.get("eligible", False):
            reason = eligibility.get(
                "reason", "You are not eligible for this tournament"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=reason,
            )

        participant = tournament_crud.register_participant(
            db=db,
            tournament_id=tournament_id,
            user_id=current_user.id,
            category=registration_data.category,
        )

        if not participant:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to register. Please try again.",
            )

        return TournamentParticipantResponse(
            id=participant.id,
            user_id=participant.user_id,
            user_name=participant.user.full_name,
            user_email=participant.user.email,
            category=participant.category_config.category,
            seed=participant.seed,
            elo_rating=participant.elo_rating,
            registration_date=participant.registration_date,
            is_active=participant.is_active,
            match_teams=participant.match_teams,
        )
    # Team registration for other tournament types
    if not registration_data.team_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Team ID is required for this tournament type",
        )

    eligibility = tournament_crud.check_team_eligibility(
        db=db, tournament_id=tournament_id, team_id=registration_data.team_id
    )

    if not eligibility.get("eligible", False):
        reason = eligibility.get("reason", "Team is not eligible for this tournament")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=reason,
        )

    team_data = TournamentTeamCreate(
        team_id=registration_data.team_id, category=registration_data.category
    )

    tournament_team = tournament_crud.register_team(
        db=db, tournament_id=tournament_id, team_data=team_data
    )

    if not tournament_team:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to register team. Please try again.",
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
        players=[
            {"id": p.id, "name": p.full_name, "elo": p.elo_rating}
            for p in tournament_team.team.players
        ],
    )


@router.delete("/{tournament_id}/teams/{team_id}")
async def unregister_team(
    tournament_id: int,
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Unregister team from tournament"""
    success = tournament_crud.unregister_team(
        db=db, tournament_id=tournament_id, team_id=team_id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team registration not found"
        )

    return {"message": "Team unregistered successfully"}


@router.get("/{tournament_id}/teams", response_model=list[TournamentTeamResponse])
async def get_tournament_teams(
    tournament_id: int,
    category: Optional[TournamentCategory] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get registered teams for tournament"""
    teams = tournament_crud.get_tournament_teams(
        db=db, tournament_id=tournament_id, category=category
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
            ],
        )
        for team in teams
    ]


@router.get(
    "/{tournament_id}/participants", response_model=list[TournamentParticipantResponse]
)
async def get_tournament_participants(
    tournament_id: int,
    category: Optional[TournamentCategory] = Query(None),
    db: Session = Depends(get_db),
):
    """Get registered participants for Americano tournaments"""
    participants = tournament_crud.get_tournament_participants(
        db=db, tournament_id=tournament_id, category=category
    )

    return [
        TournamentParticipantResponse(
            id=participant.id,
            user_id=participant.user_id,
            user_name=participant.user.full_name,
            user_email=participant.user.email,
            category=participant.category_config.category,
            seed=participant.seed,
            elo_rating=participant.elo_rating,
            registration_date=participant.registration_date,
            is_active=participant.is_active,
            match_teams=participant.match_teams,
        )
        for participant in participants
    ]


@router.post("/{tournament_id}/generate-bracket")
async def generate_tournament_bracket(
    tournament_id: int,
    category_config_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Generate tournament bracket (Admin only)"""
    # Check if user owns a club or is a club admin
    club_id = None
    if current_user.owned_club:
        club_id = current_user.owned_club.id
    else:
        # Check if user is a club admin
        club_admin = (
            db.query(ClubAdmin).filter(ClubAdmin.user_id == current_user.id).first()
        )
        if club_admin:
            club_id = club_admin.club_id

    if not club_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only club administrators can perform this action",
        )

    # Verify tournament belongs to admin's club
    tournament = tournament_crud.get_tournament(db=db, tournament_id=tournament_id)
    if not tournament or tournament.club_id != club_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tournament not found"
        )

    bracket = tournament_service.generate_bracket(
        db=db, tournament_id=tournament_id, category_config_id=category_config_id
    )

    if not bracket:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to generate bracket"
        )

    return bracket


@router.get("/{tournament_id}/bracket", response_model=TournamentBracket)
async def get_tournament_bracket(
    tournament_id: int,
    category_config_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get tournament bracket"""
    bracket = tournament_service.get_tournament_bracket(
        db=db, tournament_id=tournament_id, category_config_id=category_config_id
    )

    if not bracket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bracket not found"
        )

    return bracket


@router.get("/{tournament_id}/matches", response_model=list[TournamentMatchResponse])
async def get_tournament_matches(
    tournament_id: int,
    category: Optional[TournamentCategory] = Query(None),
    db: Session = Depends(get_db),
):
    """Get tournament matches (public endpoint)"""
    matches = tournament_crud.get_tournament_matches(
        db=db, tournament_id=tournament_id, category=category
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
            loser_advances_to_match_id=match.loser_advances_to_match_id,
        )
        for match in matches
    ]


@router.put("/matches/{match_id}", response_model=TournamentMatchResponse)
async def update_match_result(
    match_id: int,
    match_data: TournamentMatchUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update match result (Admin only)"""
    # Check if user owns a club or is a club admin
    club_id = None
    if current_user.owned_club:
        club_id = current_user.owned_club.id
    else:
        # Check if user is a club admin
        club_admin = (
            db.query(ClubAdmin).filter(ClubAdmin.user_id == current_user.id).first()
        )
        if club_admin:
            club_id = club_admin.club_id

    if not club_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only club administrators can perform this action",
        )

    # Verify match belongs to admin's club tournament
    match = tournament_crud.get_match(db=db, match_id=match_id)
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Match not found"
        )

    tournament = tournament_crud.get_tournament(
        db=db, tournament_id=match.tournament_id
    )
    if not tournament or tournament.club_id != club_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    updated_match = tournament_crud.update_match(
        db=db, match_id=match_id, match_data=match_data
    )

    if not updated_match:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to update match"
        )

    # If match is completed, advance winner and update ELO ratings
    if match_data.winning_team_id and match_data.status == "COMPLETED":
        tournament_service.advance_winner(
            db=db, match_id=match_id, winning_team_id=match_data.winning_team_id
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
        loser_advances_to_match_id=updated_match.loser_advances_to_match_id,
    )


@router.get("/{tournament_id}/eligibility/{team_id}")
async def check_team_eligibility(
    tournament_id: int,
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Check team eligibility for tournament"""
    return tournament_crud.check_team_eligibility(
        db=db, tournament_id=tournament_id, team_id=team_id
    )


@router.get("/{tournament_id}/stats", response_model=TournamentStats)
async def get_tournament_stats(
    tournament_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get tournament statistics"""
    stats = tournament_crud.get_tournament_stats(db=db, tournament_id=tournament_id)

    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tournament not found"
        )

    return TournamentStats(**stats)


@router.post("/{tournament_id}/finalize")
async def finalize_tournament(
    tournament_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Finalize tournament and award trophies (Admin only)"""
    # Check if user owns a club or is a club admin
    club_id = None
    if current_user.owned_club:
        club_id = current_user.owned_club.id
    else:
        # Check if user is a club admin
        club_admin = (
            db.query(ClubAdmin).filter(ClubAdmin.user_id == current_user.id).first()
        )
        if club_admin:
            club_id = club_admin.club_id

    if not club_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only club administrators can perform this action",
        )

    # Verify tournament belongs to admin's club
    tournament = tournament_crud.get_tournament(db=db, tournament_id=tournament_id)
    if not tournament or tournament.club_id != club_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tournament not found"
        )

    success = tournament_service.finalize_tournament(db=db, tournament_id=tournament_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to finalize tournament",
        )

    return {"message": "Tournament finalized successfully"}


# New tournament scheduling endpoints
@router.post("/{tournament_id}/schedule", response_model=TournamentScheduleResponse)
async def create_tournament_schedule(
    tournament_id: int,
    schedule_request: TournamentScheduleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create tournament schedule with hourly time slots (Admin only)"""
    # Check if user owns a club or is a club admin
    club_id = None
    if current_user.owned_club:
        club_id = current_user.owned_club.id
    else:
        club_admin = (
            db.query(ClubAdmin).filter(ClubAdmin.user_id == current_user.id).first()
        )
        if club_admin:
            club_id = club_admin.club_id

    if not club_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only club administrators can perform this action",
        )

    # Verify tournament belongs to admin's club
    tournament = tournament_crud.get_tournament(db=db, tournament_id=tournament_id)
    if not tournament or tournament.club_id != club_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tournament not found"
        )

    try:
        # Convert time slots to dictionary format
        time_slots = [
            {
                "start_time": slot.start_time,
                "end_time": slot.end_time,
                "day": slot.start_time.date(),
                "hour": slot.hour,
            }
            for slot in schedule_request.time_slots
        ]

        # Calculate tournament schedule
        schedule_result = tournament_schedule_service.calculate_tournament_schedule(
            db=db,
            tournament_id=tournament_id,
            selected_time_slots=time_slots,
            court_ids=schedule_request.court_ids,
        )

        if not schedule_result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to calculate tournament schedule",
            )

        # Create court bookings if auto_schedule is enabled
        court_bookings_created = 0
        if schedule_request.auto_schedule:
            booking_result = court_booking_service.block_courts_for_tournament(
                db=db,
                tournament_id=tournament_id,
                time_slots=time_slots,
                court_ids=schedule_request.court_ids,
            )
            court_bookings_created = booking_result["total_created"]

            if booking_result["total_failed"] > 0:
                return TournamentScheduleResponse(
                    tournament_id=tournament_id,
                    schedule=schedule_result["schedule"],
                    total_matches=schedule_result["total_matches"],
                    total_time_slots=schedule_result["total_time_slots"],
                    courts_required=schedule_result["courts_required"],
                    estimated_duration=schedule_result["estimated_duration"],
                    court_bookings_created=court_bookings_created,
                    success=False,
                    message=f"Partial success: {booking_result['total_failed']} court bookings failed",
                )

            # Update tournament with schedule info
            tournament_crud.update_tournament(
                db,
                tournament_id,
                type(
                    "obj",
                    (object,),
                    {
                        "hourly_time_slots": time_slots,
                        "assigned_court_ids": schedule_request.court_ids,
                        "schedule_generated": True,
                    },
                )(),
            )

        return TournamentScheduleResponse(
            tournament_id=tournament_id,
            schedule=schedule_result["schedule"],
            total_matches=schedule_result["total_matches"],
            total_time_slots=schedule_result["total_time_slots"],
            courts_required=schedule_result["courts_required"],
            estimated_duration=schedule_result["estimated_duration"],
            court_bookings_created=court_bookings_created,
            success=True,
            message="Tournament schedule created successfully",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create tournament schedule: {e!s}",
        )


@router.post(
    "/schedule/calculate", response_model=TournamentScheduleCalculationResponse
)
async def calculate_tournament_schedule(
    calculation_request: TournamentScheduleCalculation,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Calculate optimal tournament schedule without creating it (Admin only)"""
    club_admin_user, club_admin = get_club_admin_user(db, current_user)

    try:
        # Convert time slots to dictionary format
        time_slots = [
            {
                "start_time": slot.start_time,
                "end_time": slot.end_time,
            }
            for slot in calculation_request.time_slots
        ]

        result = tournament_schedule_service.get_optimal_court_allocation(
            db=db,
            tournament_type=calculation_request.tournament_type,
            categories=calculation_request.categories,
            participants_per_category=calculation_request.participants_per_category,
            available_courts=calculation_request.available_courts,
            time_slots=time_slots,
        )

        # Check feasibility
        total_matches = result["total_matches"]
        total_slots = result["total_time_slots"]
        courts_per_slot = result["courts_per_slot"]
        max_matches_possible = total_slots * courts_per_slot

        feasible = total_matches <= max_matches_possible
        warnings = []

        if not feasible:
            warnings.append(
                f"Not enough slots: need {total_matches} matches but can only fit {max_matches_possible}"
            )

        if len(calculation_request.available_courts) < courts_per_slot:
            warnings.append(
                f"Recommended {courts_per_slot} courts but only {len(calculation_request.available_courts)} available"
            )

        return TournamentScheduleCalculationResponse(
            total_matches=result["total_matches"],
            matches_per_category=result["matches_per_category"],
            courts_per_slot=result["courts_per_slot"],
            total_time_slots=result["total_time_slots"],
            recommended_courts=result["recommended_courts"],
            feasible=feasible,
            warnings=warnings,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to calculate tournament schedule: {e!s}",
        )


@router.post("/courts/availability", response_model=CourtAvailabilityResponse)
async def check_court_availability(
    availability_request: CourtAvailabilityRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Check court availability for tournament scheduling (Admin only)"""
    club_admin_user, club_admin = get_club_admin_user(db, current_user)

    try:
        # Convert time slots to dictionary format
        time_slots = [
            {
                "start_time": slot.start_time,
                "end_time": slot.end_time,
            }
            for slot in availability_request.time_slots
        ]

        availability = court_booking_service.check_courts_availability_for_tournament(
            db=db,
            time_slots=time_slots,
            court_ids=availability_request.court_ids,
            exclude_tournament_id=availability_request.exclude_tournament_id,
        )

        return CourtAvailabilityResponse(
            available_courts=availability["available_courts"],
            unavailable_courts=availability["unavailable_courts"],
            availability_details=availability["availability_details"],
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to check court availability: {e!s}",
        )


@router.post(
    "/{tournament_id}/courts/block", response_model=TournamentCourtBookingBulkResponse
)
async def block_tournament_courts(
    tournament_id: int,
    booking_request: TournamentCourtBookingBulkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Block courts for tournament (Admin only)"""
    club_admin_user, club_admin = get_club_admin_user(db, current_user)

    # Verify tournament belongs to admin's club
    tournament = tournament_crud.get_tournament(db=db, tournament_id=tournament_id)
    if not tournament or tournament.club_id != club_admin.club_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tournament not found"
        )

    try:
        # Convert booking data to dictionary format
        court_bookings = [
            {
                "court_id": booking.court_id,
                "start_time": booking.start_time,
                "end_time": booking.end_time,
            }
            for booking in booking_request.court_bookings
        ]

        result = court_booking_service.create_bulk_tournament_bookings(
            db=db, tournament_id=tournament_id, court_bookings=court_bookings
        )

        return TournamentCourtBookingBulkResponse(
            tournament_id=tournament_id,
            created_bookings=[
                {
                    "id": booking.id,
                    "court_id": booking.court_id,
                    "court_name": booking.court.name if booking.court else "",
                    "start_time": booking.start_time,
                    "end_time": booking.end_time,
                    "is_occupied": booking.is_occupied,
                    "match_id": booking.match_id,
                }
                for booking in result["created_bookings"]
            ],
            failed_bookings=result["failed_bookings"],
            total_created=result["total_created"],
            total_failed=result["total_failed"],
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to block courts: {e!s}",
        )


@router.delete("/{tournament_id}/courts/release")
async def release_tournament_courts(
    tournament_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Release all court bookings for tournament (Admin only)"""
    club_admin_user, club_admin = get_club_admin_user(db, current_user)

    # Verify tournament belongs to admin's club
    tournament = tournament_crud.get_tournament(db=db, tournament_id=tournament_id)
    if not tournament or tournament.club_id != club_admin.club_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tournament not found"
        )

    try:
        success = court_booking_service.release_tournament_bookings(
            db=db, tournament_id=tournament_id
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to release court bookings",
            )

        # Update tournament schedule flag
        tournament_crud.update_tournament(
            db,
            tournament_id,
            type("obj", (object,), {"schedule_generated": False})(),
        )

        return {"message": "Court bookings released successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to release courts: {e!s}",
        )


@router.post("/{tournament_id}/cancel")
async def cancel_tournament(
    tournament_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Cancel tournament and release all court bookings (Admin only)"""
    club_admin_user, club_admin = get_club_admin_user(db, current_user)

    # Verify tournament belongs to admin's club
    tournament = tournament_crud.get_tournament(db=db, tournament_id=tournament_id)
    if not tournament or tournament.club_id != club_admin.club_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tournament not found"
        )

    try:
        success = tournament_service.cancel_tournament(
            db=db, tournament_id=tournament_id
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to cancel tournament",
            )

        return {"message": "Tournament cancelled successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to cancel tournament: {e!s}",
        )


@router.get(
    "/{tournament_id}/schedule/summary", response_model=TournamentScheduleSummary
)
async def get_tournament_schedule_summary(
    tournament_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get tournament schedule summary (Admin only)"""
    club_admin_user, club_admin = get_club_admin_user(db, current_user)

    # Verify tournament belongs to admin's club
    tournament = tournament_crud.get_tournament(db=db, tournament_id=tournament_id)
    if not tournament or tournament.club_id != club_admin.club_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tournament not found"
        )

    try:
        summary = tournament_schedule_service.get_tournament_schedule_summary(
            db=db, tournament_id=tournament_id
        )

        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tournament schedule not found",
            )

        return TournamentScheduleSummary(**summary)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get tournament schedule summary: {e!s}",
        )
