from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import get_db
from app.core import security
from app.services import file_service
from app.crud.tournament_crud import tournament_crud

router = APIRouter()

@router.get("/me", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(security.get_current_active_user)):
    """
    Get current user's profile.
    """
    return current_user

@router.put("/me", response_model=schemas.User)
async def update_user_me(
    user_in: schemas.UserUpdate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(security.get_current_active_user)
):
    """
    Update current user's profile.
    """
    return crud.user_crud.update_user(db=db, db_user=current_user, user_in=user_in)

@router.post("/me/profile-picture", response_model=schemas.User)
async def upload_profile_picture(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user)
):
    """
    Upload a profile picture for the current user.
    """
    try:
        # Upload image and get the URL
        image_url = await file_service.save_profile_picture(file=file, user_id=current_user.id)
        
        # Update user's profile_picture_url in the database
        user_update_schema = schemas.UserUpdate(profile_picture_url=image_url)
        updated_user = crud.user_crud.update_user(db=db, db_user=current_user, user_in=user_update_schema)
        
        return updated_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Generic error for other issues (e.g., cloud storage connection)
        raise HTTPException(status_code=500, detail="An error occurred during file upload.")

@router.get("/me/elo-adjustment-requests", response_model=List[schemas.EloAdjustmentRequest])
async def read_user_elo_adjustment_requests(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user)
):
    """
    Retrieve ELO adjustment requests for the current user.
    """
    return crud.elo_adjustment_request_crud.get_elo_adjustment_requests_by_user(db, user_id=current_user.id)

@router.get("/search", response_model=List[schemas.UserSearchResult])
async def search_users(
    query: str = Query(..., min_length=2, max_length=50),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user)
):
    """
    Search for users by name or email.
    """
    users = crud.user_crud.search_users(db, query=query, limit=limit, current_user_id=current_user.id)
    return users

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
        db=db, 
        request=request, 
        user_id=user_id,
        current_elo=current_elo
    )
    return {"message": "ELO adjustment request submitted successfully."}

@router.get("/{user_id}/trophies", response_model=List[schemas.TournamentTrophyResponse])
async def get_user_trophies(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user)
):
    """
    Get tournament trophies for a user.
    """
    # Allow users to see their own trophies, or make this public if desired
    if current_user.id != user_id:
        # For now, only allow users to see their own trophies
        # In the future, this could be made public or restricted to friends/teammates
        raise HTTPException(
            status_code=403,
            detail="You can only view your own trophies."
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
            awarded_at=trophy.awarded_at
        )
        for trophy in trophies
    ] 