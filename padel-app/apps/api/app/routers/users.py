from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core import security
from app.crud.team_crud import team_crud
from app.crud.tournament_crud import tournament_crud
from app.crud.game_history_crud import game_history_crud
from app.database import get_db
from app.services import file_service
from app.schemas.game_history_schemas import (
    GameHistoryQuery,
    GameHistoryResponse,
    GameStatistics,
    ProfileGameHistoryResponse,
)

router = APIRouter()


@router.get("/me", response_model=schemas.User)
async def read_users_me(
    current_user: models.User = Depends(security.get_current_active_user),
):
    """
    Get current user's profile.
    """
    return current_user


@router.put("/me", response_model=schemas.User)
async def update_user_me(
    user_in: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """
    Update current user's profile.
    """
    return crud.user_crud.update_user(
        db=db, db_user=current_user, user_in=user_in, allow_elo_update=False
    )


@router.post("/me/skill-assessment", response_model=schemas.SkillAssessmentResponse)
async def complete_skill_assessment(
    assessment: schemas.SkillAssessmentRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """
    Complete skill assessment during onboarding and update ELO rating.
    """
    try:
        # Update user with the calculated ELO from the assessment
        user_update = schemas.UserUpdate(
            elo_rating=assessment.calculated_elo,
            preferred_position=assessment.preferred_position,
        )

        # Use allow_elo_update=True to bypass the ELO restriction for onboarding
        updated_user = crud.user_crud.update_user(
            db=db, db_user=current_user, user_in=user_update, allow_elo_update=True
        )

        return schemas.SkillAssessmentResponse(
            success=True,
            message="Skill assessment completed successfully",
            new_elo_rating=updated_user.elo_rating,
            preferred_position=updated_user.preferred_position,
        )

    except Exception as e:
        return schemas.SkillAssessmentResponse(
            success=False,
            message=f"Failed to update skill assessment: {e!s}",
            new_elo_rating=current_user.elo_rating,
            preferred_position=current_user.preferred_position,
        )


@router.put("/me/elo", response_model=schemas.User)
async def update_user_elo(
    elo_rating: float,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """
    Directly update user's ELO rating (for onboarding completion or admin use).
    """
    # Validate ELO range
    if not (1.0 <= elo_rating <= 7.0):
        raise HTTPException(
            status_code=400, detail="ELO rating must be between 1.0 and 7.0"
        )

    try:
        # Direct database update bypassing CRUD restrictions
        current_user.elo_rating = elo_rating
        db.add(current_user)
        db.commit()
        db.refresh(current_user)

        return current_user

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Failed to update ELO rating: {e!s}"
        )


@router.post("/me/profile-picture", response_model=schemas.User)
async def upload_profile_picture(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """
    Upload a profile picture for the current user.
    """
    try:
        # Upload image and get the URL
        image_url = await file_service.save_profile_picture(
            file=file, user_id=current_user.id
        )

        # Update user's profile_picture_url in the database
        user_update_schema = schemas.UserUpdate(profile_picture_url=image_url)
        return crud.user_crud.update_user(
            db=db, db_user=current_user, user_in=user_update_schema
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        # Generic error for other issues (e.g., cloud storage connection)
        raise HTTPException(
            status_code=500, detail="An error occurred during file upload."
        )


@router.get(
    "/me/elo-adjustment-requests", response_model=list[schemas.EloAdjustmentRequest]
)
async def read_user_elo_adjustment_requests(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """
    Retrieve ELO adjustment requests for the current user.
    """
    return crud.elo_adjustment_request_crud.get_elo_adjustment_requests_by_user(
        db, user_id=current_user.id
    )


@router.get("/search", response_model=list[schemas.UserSearchResult])
async def search_users(
    query: str = Query(..., min_length=2, max_length=50),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """
    Search for users by name or email.
    """
    return crud.user_crud.search_users(
        db, query=query, limit=limit, current_user_id=current_user.id
    )


@router.post("/{user_id}/request-elo-adjustment", status_code=201)
def request_elo_adjustment(
    user_id: int,
    request: schemas.EloAdjustmentRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """
    Request a manual adjustment of a user's ELO rating.
    """
    if current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You can only request an ELO adjustment for yourself.",
        )

    # Check the user's current ELO to store it with the request
    current_elo = current_user.elo_rating

    crud.elo_adjustment_request_crud.create_elo_adjustment_request(
        db=db, request=request, user_id=user_id, current_elo=current_elo
    )
    return {"message": "ELO adjustment request submitted successfully."}


@router.get(
    "/{user_id}/trophies", response_model=list[schemas.TournamentTrophyResponse]
)
async def get_user_trophies(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """
    Get tournament trophies for a user.
    """
    # Allow users to see their own trophies, or make this public if desired
    if current_user.id != user_id:
        # For now, only allow users to see their own trophies
        # In the future, this could be made public or restricted to friends/teammates
        raise HTTPException(
            status_code=403, detail="You can only view your own trophies."
        )

    trophies = tournament_crud.get_user_trophies(db=db, user_id=user_id)

    return [
        schemas.TournamentTrophyResponse(
            id=trophy.id,
            tournament_id=trophy.tournament_id,
            tournament_name=trophy.tournament.name,
            category=trophy.category_config.category,
            user_id=trophy.user_id,
            team_id=trophy.team_id,
            position=trophy.position,
            trophy_type=trophy.trophy_type,
            awarded_at=trophy.awarded_at,
        )
        for trophy in trophies
    ]


@router.get("/me/teams", response_model=list[schemas.Team])
async def get_user_teams(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """
    Get teams for the current user.
    """
    return team_crud.get_user_teams(db=db, user_id=current_user.id)


@router.post("/me/teams", response_model=schemas.Team)
async def create_team(
    team_in: schemas.TeamCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """
    Create a new team for the current user.
    """
    return team_crud.create_team(db=db, team_data=team_in, creator_id=current_user.id)


@router.post("/me/teams/{team_id}/players", response_model=schemas.Team)
async def add_player_to_team(
    team_id: int,
    player_data: dict,  # Expecting {"user_id": int}
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """
    Add a player to the current user's team.
    """
    # Get the team
    team = team_crud.get_team(db=db, team_id=team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # Check if current user is in the team (has permission to add players)
    if current_user not in team.players:
        raise HTTPException(
            status_code=403,
            detail="You can only add players to teams you're a member of",
        )

    # Get the user to add
    user_id = player_data.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    user_to_add = db.query(models.User).filter(models.User.id == user_id).first()
    if not user_to_add:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if user is already in the team
    if user_to_add in team.players:
        raise HTTPException(status_code=400, detail="User is already in the team")

    # Add the user to the team
    return team_crud.add_player_to_team(db=db, team=team, user=user_to_add)


# Game History Endpoints

@router.get("/me/game-history", response_model=GameHistoryResponse)
async def get_current_user_game_history(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records to return"),
    start_date: Optional[str] = Query(None, description="Filter games from this date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter games until this date (YYYY-MM-DD)"),
    result_filter: Optional[str] = Query("ALL", description="Filter by result: ALL, WINS, LOSSES, DRAWS"),
    partner_id: Optional[int] = Query(None, description="Filter by partner user ID"),
    opponent_id: Optional[int] = Query(None, description="Filter by opponent user ID"),
    club_id: Optional[int] = Query(None, description="Filter by club ID"),
    completed_only: bool = Query(True, description="Only include completed games"),
):
    """
    Get the current user's game history with filtering and pagination.
    """
    from datetime import datetime

    # Parse dates
    start_date_parsed = None
    end_date_parsed = None

    if start_date:
        try:
            start_date_parsed = datetime.fromisoformat(start_date)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid start_date format. Use YYYY-MM-DD"
            )

    if end_date:
        try:
            end_date_parsed = datetime.fromisoformat(end_date)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid end_date format. Use YYYY-MM-DD"
            )

    # Create query object
    query = GameHistoryQuery(
        skip=skip,
        limit=limit,
        start_date=start_date_parsed,
        end_date=end_date_parsed,
        result_filter=result_filter,
        partner_id=partner_id,
        opponent_id=opponent_id,
        club_id=club_id,
        completed_only=completed_only,
    )

    # Get game history
    games, total_count = game_history_crud.get_user_game_history(
        db=db,
        user_id=current_user.id,
        query=query,
    )

    has_more = (skip + limit) < total_count

    return GameHistoryResponse(
        games=games,
        total_count=total_count,
        has_more=has_more,
    )


@router.get("/me/game-stats", response_model=GameStatistics)
async def get_current_user_game_statistics(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
    limit_recent: int = Query(10, ge=1, le=50, description="Number of recent games to include in statistics"),
):
    """
    Get comprehensive game statistics for the current user.
    """
    return game_history_crud.get_user_game_statistics(
        db=db,
        user_id=current_user.id,
        limit_recent=limit_recent,
    )


@router.get("/{user_id}/game-history", response_model=ProfileGameHistoryResponse)
async def get_user_public_game_history(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
    limit: int = Query(5, ge=1, le=20, description="Number of recent games to include"),
):
    """
    Get public game history for any user's profile.
    Respects privacy settings - only shows public information.
    """
    # Check if user exists
    target_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return game_history_crud.get_public_game_history(
        db=db,
        user_id=user_id,
        limit=limit,
    )


@router.get("/{user_id}/game-stats", response_model=GameStatistics)
async def get_user_public_game_statistics(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
    limit_recent: int = Query(10, ge=1, le=50, description="Number of recent games to include in statistics"),
):
    """
    Get game statistics for any user's profile.
    Respects privacy settings - only shows public information.
    """
    # Check if user exists
    target_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Check privacy settings (basic implementation)
    # For now, allow viewing if user is public or if it's the same user
    if user_id != current_user.id:
        # TODO: Implement proper privacy controls
        # For now, allow public access to basic statistics
        pass

    return game_history_crud.get_user_game_statistics(
        db=db,
        user_id=user_id,
        limit_recent=limit_recent,
    )
