from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import get_db
from app.core import security
from app.services import file_service

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
    crud.elo_adjustment_request_crud.create_elo_adjustment_request(
        db=db, request=request, user_id=user_id
    )
    return {"message": "ELO adjustment request submitted successfully."} 