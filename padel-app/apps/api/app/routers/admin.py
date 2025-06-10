from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.schemas import court_schemas, club_schemas, booking_schemas, user_schemas
from app import crud
from app.database import get_db
from app.models import User, UserRole, BookingStatus
from app.core.security import get_current_active_user
from app.services import file_service
from app.core.dependencies import RoleChecker

router = APIRouter(
    tags=["admin"],
    dependencies=[Depends(RoleChecker([UserRole.CLUB_ADMIN]))],
)

async def get_current_admin_user(current_user: User = Depends(get_current_active_user)):
    return current_user

# Example of a protected route
@router.get("/test", response_model=user_schemas.User)
async def test_admin_route(current_admin: User = Depends(get_current_admin_user)):
    """
    Test route to verify that the admin authentication is working.
    
    This endpoint is protected and only accessible by users with the `CLUB_ADMIN` role.
    It returns the user object of the authenticated admin.
    """
    return current_admin

@router.get("/my-club", response_model=club_schemas.Club)
async def read_owned_club(
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Retrieve the club owned by the current admin user.
    
    This endpoint returns the full details of the club associated with the authenticated admin.
    If the admin does not own a club, it returns a 404 error.
    """
    if not current_admin.owned_club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The current admin does not own a club."
        )
    return current_admin.owned_club

@router.put("/my-club", response_model=club_schemas.Club)
async def update_owned_club(
    *,
    db: Session = Depends(get_db),
    club_in: club_schemas.ClubUpdate,
    current_admin: User = Depends(get_current_admin_user),
):
    """
    Update the club owned by the current admin user.
    
    This endpoint allows an admin to update the details of their own club.
    The request body should contain the fields to be updated.
    If the admin does not own a club, it returns a 404 error.
    """
    club = current_admin.owned_club
    if not club:
        raise HTTPException(
            status_code=404,
            detail="The current admin does not own a club to update.",
        )
    club = crud.club_crud.update_club(db=db, db_obj=club, obj_in=club_in)
    return club

@router.get("/my-club/courts", response_model=List[court_schemas.Court])
async def read_owned_club_courts(
    current_admin: User = Depends(get_current_admin_user),
):
    """
    Retrieve the courts for the club owned by the current admin user.
    
    This endpoint returns a list of all courts associated with the authenticated admin's club.
    If the admin does not own a club, it returns a 404 error.
    """
    club = current_admin.owned_club
    if not club:
        raise HTTPException(
            status_code=404,
            detail="The current admin does not own a club.",
        )
    return club.courts

@router.post("/my-club/courts", response_model=court_schemas.Court)
async def create_owned_club_court(
    *,
    db: Session = Depends(get_db),
    court_in: court_schemas.CourtCreateForAdmin,
    current_admin: User = Depends(get_current_admin_user),
):
    """
    Create a new court for the club owned by the current admin user.
    
    This endpoint allows an admin to add a new court to their club.
    The request body should contain the details of the new court.
    If the admin does not own a club, it returns a 404 error.
    """
    club = current_admin.owned_club
    if not club:
        raise HTTPException(
            status_code=404,
            detail="The current admin does not own a club.",
        )
    court = crud.court_crud.create_court(db=db, court=court_in, club_id=club.id)
    return court

@router.put("/my-club/courts/{court_id}", response_model=court_schemas.Court)
async def update_owned_club_court(
    *,
    db: Session = Depends(get_db),
    court_id: int,
    court_in: court_schemas.CourtUpdate,
    current_admin: User = Depends(get_current_admin_user),
):
    """
    Update a court for the club owned by the current admin user.
    
    This endpoint allows an admin to update the details of a specific court in their club.
    The admin must own the club to which the court belongs.
    If the court is not found or does not belong to the admin's club, it returns a 404 error.
    """
    club = current_admin.owned_club
    if not club:
        raise HTTPException(
            status_code=404,
            detail="The current admin does not own a club.",
        )
    
    court = crud.court_crud.get_court(db=db, court_id=court_id)
    if not court or court.club_id != club.id:
        raise HTTPException(
            status_code=404,
            detail="Court not found or not owned by the admin's club.",
        )

    court = crud.court_crud.update_court(db=db, db_obj=court, obj_in=court_in)
    return court

@router.delete("/my-club/courts/{court_id}", response_model=court_schemas.Court)
async def delete_owned_club_court(
    *,
    db: Session = Depends(get_db),
    court_id: int,
    current_admin: User = Depends(get_current_admin_user),
):
    """
    Delete a court from the club owned by the current admin user.
    
    This endpoint allows an admin to delete a specific court from their club.
    The admin must own the club to which the court belongs.
    If the court is not found or does not belong to the admin's club, it returns a 404 error.
    """
    club = current_admin.owned_club
    if not club:
        raise HTTPException(
            status_code=404,
            detail="The current admin does not own a club.",
        )
    
    court = crud.court_crud.get_court(db=db, court_id=court_id)
    if not court or court.club_id != club.id:
        raise HTTPException(
            status_code=404,
            detail="Court not found or not owned by the admin's club.",
        )

    court = crud.court_crud.remove_court(db=db, court_id=court_id)
    return court

@router.get("/my-club/bookings", response_model=List[booking_schemas.Booking])
async def read_owned_club_bookings(
    *,
    db: Session = Depends(get_db),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    court_id: Optional[int] = None,
    status: Optional[BookingStatus] = None,
    skip: int = 0,
    limit: int = 100,
    current_admin: User = Depends(get_current_admin_user),
):
    """
    Retrieve bookings for the club owned by the current admin user.
    
    This endpoint returns a list of bookings for the admin's club, with optional filtering.
    Admins can filter bookings by date range, court, and status.
    If the admin does not own a club, it returns a 404 error.
    """
    club = current_admin.owned_club
    if not club:
        raise HTTPException(
            status_code=404,
            detail="The current admin does not own a club.",
        )
    
    bookings = crud.booking_crud.get_bookings_by_club(
        db,
        club_id=club.id,
        skip=skip,
        limit=limit,
        start_date_filter=start_date,
        end_date_filter=end_date,
        court_id_filter=court_id,
        status_filter=status,
    )
    return bookings

@router.post("/my-club/profile-picture", response_model=club_schemas.Club)
async def upload_club_profile_picture(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
    file: UploadFile = File(...)
):
    """
    Upload a profile picture for the admin's club.
    """
    club = current_admin.owned_club
    if not club:
        raise HTTPException(
            status_code=404,
            detail="The current admin does not own a club.",
        )

    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Only images are allowed.")

    try:
        file_url = file_service.save_club_picture(file=file, club_id=club.id)
        
        club_update_data = club_schemas.ClubUpdate(image_url=file_url)
        
        updated_club = crud.club_crud.update_club(db=db, db_obj=club, obj_in=club_update_data)
        
        return updated_club
    except IOError as e:
        raise HTTPException(status_code=500, detail=f"Could not save club picture: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during club picture upload: {e}")

@router.post("/my-club", response_model=club_schemas.Club, status_code=status.HTTP_201_CREATED)
async def create_my_club(
    club_in: club_schemas.ClubCreateForAdmin,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user),
):
    """
    Create a new club for the current admin user.
    """
    if current_admin.owned_club:
        raise HTTPException(
            status_code=400,
            detail="This admin already owns a club.",
        )
    
    new_club = crud.club_crud.create_club(db=db, club=club_in, owner_id=current_admin.id)
    return new_club 