from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import date

from app import schemas, crud, models
from app.database import get_db
from app.services import availability_service
from app.core import security

router = APIRouter()

@router.post("", response_model=schemas.Court, status_code=status.HTTP_201_CREATED)
def create_court_for_club(
    court_in: schemas.CourtCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """
    Create a new court for the authenticated user's club.
    The user must be a club admin and must own the club specified in the request.
    """
    # Authorization: Check if the current user is the owner of the specified club
    if not current_user.owned_club or current_user.owned_club.id != court_in.club_id:
        if current_user.role != models.UserRole.SUPER_ADMIN: # Super admin can create for any club
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to add a court to this club.",
            )

    new_court = crud.court_crud.create_court(
        db=db, court_in=court_in, club_id=court_in.club_id
    )
    return new_court

@router.get("/{court_id}/availability", response_model=List[schemas.TimeSlot])
async def get_court_availability_slots(
    court_id: int,
    target_date: date = Query(..., description="Target date in YYYY-MM-DD format"), # `date` type automatically handles parsing
    db: Session = Depends(get_db)
):
    """
    Retrieve available 30-minute time slots for a specific court on a given date.
    """
    # First, check if the court exists to provide a clear 404 if not
    court = crud.court_crud.get_court(db, court_id=court_id)
    if not court:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Court with id {court_id} not found"
        )
    
    try:
        availability = availability_service.get_court_availability(
            db=db, court_id=court_id, target_date=target_date
        )
        return availability
    except Exception as e:
        # Log the exception e for debugging purposes
        print(f"Error calculating availability for court {court_id} on {target_date}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while calculating court availability."
        ) 