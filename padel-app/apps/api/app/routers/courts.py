from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import date

from app import schemas, crud, models
from app.database import get_db
from app.services import availability_service
from app.core import security
from app.schemas import BookingTimeSlot

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

@router.get("", response_model=List[schemas.Court])
def get_courts_for_club(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """
    Get all courts for the authenticated user's club.
    The user must be a club admin.
    """
    # Check if user has a club (either owned or admin of)
    club_id = None
    if current_user.owned_club:
        club_id = current_user.owned_club.id
    else:
        # Check if user is a club admin
        club_admin = db.query(models.ClubAdmin).filter(models.ClubAdmin.user_id == current_user.id).first()
        if club_admin:
            club_id = club_admin.club_id
    
    if not club_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be associated with a club to view courts.",
        )
    
    courts = crud.court_crud.get_courts_by_club(db=db, club_id=club_id)
    return courts

@router.get(
    "/{court_id}/availability",
    response_model=List[schemas.BookingTimeSlot],
    dependencies=[Depends(security.get_current_active_user)],
    summary="Get Court Availability",
    description="Retrieve the availability for a specific court for a given date.",
)
def get_court_availability(
    court_id: int,
    date: date,
    duration: Optional[int] = Query(90, enum=[60, 90]),
    db: Session = Depends(get_db),
):
    court = crud.court_crud.get_court(db, court_id=court_id)
    if not court:
        raise HTTPException(status_code=404, detail="Court not found")

    try:
        availability_slots = availability_service.get_court_availability_for_day(
            db=db, court_id=court_id, target_date=date, duration=duration
        )
        return availability_slots
    except Exception as e:
        print(e) # Temporary print for debugging
        # It's good practice to log the error.
        # import logging
        # logging.error(f"Error fetching availability for court {court_id} on {date}: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while calculating court availability."
        ) 