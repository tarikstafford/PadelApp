from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, models, schemas # models for type hints, schemas for response_model
from app.database import get_db

router = APIRouter()

@router.get("", response_model=List[schemas.Club]) # GET /clubs (pluralized by prefix later)
async def read_clubs(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0), 
    limit: int = Query(100, ge=1, le=200),
    name: Optional[str] = Query(None, min_length=1, max_length=100),
    city: Optional[str] = Query(None, min_length=1, max_length=100),
    sort_by: Optional[str] = Query(None, description="Sort by field: e.g., 'name', 'city'"),
    sort_desc: bool = Query(False, description="Sort in descending order")
):
    """
    Retrieve a list of clubs with pagination, filtering, and sorting options.
    """
    clubs = crud.club_crud.get_clubs(
        db, skip=skip, limit=limit, name=name, city=city, sort_by=sort_by, sort_desc=sort_desc
    )
    return clubs

@router.get("/{club_id}", response_model=schemas.ClubWithCourts) # GET /clubs/{club_id}
async def read_club(
    club_id: int, 
    db: Session = Depends(get_db)
):
    """
    Retrieve details for a specific club, including its courts.
    SQLAlchemy will lazy/eager load the 'courts' relationship based on access pattern or explicit options.
    Pydantic's `ClubWithCourts` schema (with `from_attributes=True`) will serialize this.
    """
    db_club = crud.club_crud.get_club(db, club_id=club_id)
    if db_club is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Club not found")
    return db_club

@router.get("/{club_id}/courts", response_model=List[schemas.Court]) # GET /clubs/{club_id}/courts
async def read_club_courts(
    club_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of courts for a specific club with pagination.
    First, check if the club exists.
    """
    db_club = crud.club_crud.get_club(db, club_id=club_id) # Verify club exists
    if db_club is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Club not found, so cannot retrieve its courts")
    
    courts = crud.court_crud.get_courts_by_club(db, club_id=club_id, skip=skip, limit=limit)
    return courts 