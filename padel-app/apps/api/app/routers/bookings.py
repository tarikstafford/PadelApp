from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import date # For deriving date from datetime

from app import crud, models, schemas # For models.User, schemas.Booking, schemas.BookingCreate
from app.database import get_db
from app.core import security # For get_current_active_user
from app.services import availability_service # For checking slot availability
# from app.services.availability_service import SLOT_INTERVAL_MINUTES # For end_time calculation if not done in CRUD

router = APIRouter()

@router.post("", response_model=schemas.Booking, status_code=status.HTTP_201_CREATED)
async def create_new_booking(
    booking_in: schemas.BookingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user)
):
    """
    Create a new booking for the current authenticated user.
    Validation for slot availability is performed here before calling CRUD.
    """
    # 1. Verify court exists
    court = crud.court_crud.get_court(db, court_id=booking_in.court_id)
    if not court:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Court with id {booking_in.court_id} not found."
        )

    # 2. Check slot availability
    target_date_val = booking_in.start_time.date()
    try:
        available_slots = availability_service.get_court_availability(
            db=db, court_id=booking_in.court_id, target_date=target_date_val
        )
    except Exception as e:
        # Log e for debugging
        print(f"Error checking availability: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check court availability."
        )

    requested_slot_available = False
    for slot in available_slots:
        if slot.start_time == booking_in.start_time and slot.is_available:
            requested_slot_available = True
            break
    
    if not requested_slot_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The requested time slot is not available or is invalid."
        )

    # 3. If slot is available, create the booking
    try:
        created_booking = crud.booking_crud.create_booking(
            db=db, booking_in=booking_in, user_id=current_user.id
        )
        return created_booking
    except Exception as e:
        # Catch any other unexpected errors during booking creation
        # Log e for debugging
        print(f"Error creating booking: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the booking."
        )

@router.get("", response_model=List[schemas.Booking])
async def read_user_bookings(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    start_date_filter: Optional[date] = Query(None, description="Filter bookings from this date (YYYY-MM-DD)"),
    end_date_filter: Optional[date] = Query(None, description="Filter bookings up to this date (YYYY-MM-DD)"),
    sort_by: Optional[str] = Query(None, description="Sort by field: e.g., 'start_time', 'status'"),
    sort_desc: bool = Query(False, description="Sort in descending order")
):
    """
    Retrieve all bookings for the current authenticated user.
    Supports pagination, date range filtering, and sorting.
    """
    try:
        bookings = crud.booking_crud.get_bookings_by_user(
            db=db, 
            user_id=current_user.id, 
            skip=skip, 
            limit=limit, 
            start_date_filter=start_date_filter, 
            end_date_filter=end_date_filter,
            sort_by=sort_by,
            sort_desc=sort_desc
        )
        return bookings
    except Exception as e:
        import traceback
        print('ERROR in /api/v1/bookings:', e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{booking_id}", response_model=schemas.Booking)
async def read_booking_details(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user)
):
    """
    Retrieve details for a specific booking made by the current authenticated user.
    """
    db_booking = crud.booking_crud.get_booking(db, booking_id=booking_id)
    if db_booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    
    # Authorization check: ensure the current user owns the booking
    # (Admin override could be added here later if needed)
    if db_booking.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this booking")
        
    return db_booking

# Future endpoints for GET /bookings, GET /bookings/{id} will go here (Subtask 7.3) 