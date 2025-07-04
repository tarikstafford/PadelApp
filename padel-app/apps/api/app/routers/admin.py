from datetime import date, datetime
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    Request,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app import crud
from app.core.dependencies import (
    booking_admin_checker,
    club_admin_checker,
    role_checker,
)
from app.core.security import get_current_active_user
from app.database import get_db
from app.models import BookingStatus, User, UserRole
from app.schemas import (
    booking_schemas,
    club_schemas,
    court_schemas,
    game_schemas,
    user_schemas,
)
from app.services import file_service

router = APIRouter(
    tags=["admin"],
    dependencies=[
        Depends(
            role_checker([UserRole.ADMIN, UserRole.SUPER_ADMIN, UserRole.CLUB_ADMIN])
        )
    ],
)


# Example of a protected route
@router.get("/test", response_model=user_schemas.User)
async def test_admin_route(current_admin: User = Depends(get_current_active_user)):
    """
    Test route to verify that the admin authentication is working.

    This endpoint is protected and only accessible by users with the `CLUB_ADMIN` role.
    It returns the user object of the authenticated admin.
    """
    return current_admin


@router.get("/my-club", response_model=club_schemas.Club)
async def read_owned_club(current_admin: User = Depends(get_current_active_user)):
    """
    Retrieve the club owned by the current admin user.

    This endpoint returns the full details of the club associated with the authenticated admin.
    If the admin does not own a club, it returns a 404 error.
    """
    if not current_admin.owned_club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The current admin does not own a club.",
        )
    return current_admin.owned_club


@router.put(
    "/club/{club_id}",
    response_model=club_schemas.Club,
    dependencies=[Depends(club_admin_checker())],
)
async def update_club(
    *,
    club_id: int,
    db: Session = Depends(get_db),
    club_in: club_schemas.ClubUpdate,
):
    """
    Update a club's details.

    This endpoint allows an admin to update the details of their own club.
    The request body should contain the fields to be updated.
    """
    club = crud.club_crud.get_club(db=db, club_id=club_id)
    if not club:
        raise HTTPException(
            status_code=404,
            detail="Club not found.",
        )
    return crud.club_crud.update_club(db=db, db_obj=club, obj_in=club_in)


@router.get(
    "/club/{club_id}",
    response_model=club_schemas.Club,
    dependencies=[Depends(club_admin_checker())],
)
async def read_club(
    club_id: int,
    db: Session = Depends(get_db),
):
    """
    Retrieve a club's details.
    """
    club = crud.club_crud.get_club(db=db, club_id=club_id)
    if not club:
        raise HTTPException(
            status_code=404,
            detail="Club not found.",
        )
    return club


@router.get(
    "/club/{club_id}/courts",
    response_model=list[court_schemas.Court],
    dependencies=[Depends(club_admin_checker())],
)
async def read_club_courts(
    club_id: int,
    db: Session = Depends(get_db),
):
    """
    Retrieve the courts for a specific club.
    """
    return crud.court_crud.get_courts_by_club(db=db, club_id=club_id)


@router.get(
    "/club/{club_id}/schedule",
    response_model=club_schemas.ScheduleResponse,
    dependencies=[Depends(club_admin_checker())],
)
async def read_club_schedule(
    club_id: int,
    start_date: Optional[date] = Query(
        None,
        description="Start date for fetching schedule. Defaults to today if no dates are provided.",
    ),
    end_date: Optional[date] = Query(
        None,
        description="End date for fetching schedule. Defaults to start_date if not provided.",
    ),
    db: Session = Depends(get_db),
):
    """
    Retrieve the courts and bookings for a specific club on a given date or date range.
    If no dates are provided, it returns the schedule for the current day.
    """
    today = date.today()
    s_date = start_date or today
    e_date = end_date or s_date

    if s_date > e_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date cannot be earlier than start date.",
        )

    courts = crud.court_crud.get_courts_by_club(db=db, club_id=club_id)
    bookings = crud.booking_crud.get_bookings_by_club(
        db, club_id=club_id, start_date_filter=s_date, end_date_filter=e_date
    )
    return {"courts": courts, "bookings": bookings}


@router.get("/my-club/schedule", response_model=club_schemas.ScheduleResponse)
async def get_my_club_schedule(
    request: Request,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_user),
):
    """
    Retrieve the schedule for the current admin's club.
    This is a convenience endpoint that gets the club_id from the session.
    It forwards any query params to the main schedule endpoint.
    """
    if not current_admin.owned_club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The current admin does not own a club.",
        )

    # Convert query params to a dictionary
    query_params = dict(request.query_params)
    start_date_str = query_params.get("start_date")
    end_date_str = query_params.get("end_date")

    s_date = None
    e_date = None

    try:
        if start_date_str:
            s_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        if end_date_str:
            e_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Please use YYYY-MM-DD.",
        )

    # Call the existing endpoint logic
    return await read_club_schedule(
        club_id=current_admin.owned_club.id, start_date=s_date, end_date=e_date, db=db
    )


@router.get("/my-club/courts", response_model=list[court_schemas.Court])
async def read_owned_club_courts(
    current_admin: User = Depends(get_current_active_user),
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
    current_admin: User = Depends(get_current_active_user),
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
    return crud.court_crud.create_court(db=db, court_in=court_in, club_id=club.id)


@router.put("/my-club/courts/{court_id}", response_model=court_schemas.Court)
async def update_owned_club_court(
    *,
    db: Session = Depends(get_db),
    court_id: int,
    court_in: court_schemas.CourtUpdate,
    current_admin: User = Depends(get_current_active_user),
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

    return crud.court_crud.update_court(db=db, db_court=court, court_in=court_in)


@router.get("/my-club/courts/{court_id}", response_model=court_schemas.Court)
async def read_owned_club_court(
    *,
    db: Session = Depends(get_db),
    court_id: int,
    current_admin: User = Depends(get_current_active_user),
):
    """
    Get a specific court for the club owned by the current admin user.
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

    return court


@router.delete(
    "/my-club/courts/{court_id}",
    response_model=court_schemas.Court,
    dependencies=[Depends(club_admin_checker())],
)
async def delete_owned_club_court(
    *,
    db: Session = Depends(get_db),
    court_id: int,
    current_admin: User = Depends(get_current_active_user),
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

    return crud.court_crud.remove_court(db=db, court_id=court_id)


@router.get("/my-club/bookings", response_model=list[booking_schemas.Booking])
async def read_owned_club_bookings(
    *,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_user),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    court_id: Optional[int] = None,
    status: Optional[BookingStatus] = None,
    skip: int = 0,
    limit: int = 100,
):
    """
    Retrieve bookings for the club owned by the current admin user.
    """
    club = current_admin.owned_club
    if not club:
        raise HTTPException(
            status_code=404,
            detail="The current admin does not own a club.",
        )

    return crud.booking_crud.get_bookings_by_club(
        db,
        club_id=club.id,
        skip=skip,
        limit=limit,
        start_date_filter=start_date,
        end_date_filter=end_date,
        court_id_filter=court_id,
        status_filter=status,
    )


@router.get(
    "/club/{club_id}/bookings",
    response_model=list[booking_schemas.Booking],
    dependencies=[Depends(club_admin_checker())],
)
async def read_club_bookings(
    *,
    club_id: int,
    db: Session = Depends(get_db),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    court_id: Optional[int] = None,
    status: Optional[BookingStatus] = None,
    skip: int = 0,
    limit: int = 100,
):
    """
    Retrieve bookings for a specific club.

    This endpoint returns a list of bookings for a club, with optional filtering.
    Admins can filter bookings by date range, court, and status.
    """
    return crud.booking_crud.get_bookings_by_club(
        db,
        club_id=club_id,
        skip=skip,
        limit=limit,
        start_date_filter=start_date,
        end_date_filter=end_date,
        court_id_filter=court_id,
        status_filter=status,
    )


@router.get(
    "/bookings/{booking_id}/game",
    response_model=game_schemas.GameResponse,
    dependencies=[Depends(booking_admin_checker())],
)
async def read_game_for_booking(
    booking_id: int,
    db: Session = Depends(get_db),
):
    """
    Retrieve the game associated with a specific booking.
    """
    game = crud.game_crud.get_game_by_booking(db, booking_id=booking_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found for this booking")
    return game


@router.post("/my-club/profile-picture", response_model=club_schemas.Club)
async def upload_club_profile_picture(
    current_admin: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
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
        raise HTTPException(
            status_code=400, detail="Invalid file type. Only images are allowed."
        )

    try:
        file_url = await file_service.save_club_picture(file=file, club_id=club.id)

        club_update_data = club_schemas.ClubUpdate(image_url=file_url)

        return crud.club_crud.update_club(db=db, db_obj=club, obj_in=club_update_data)

    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Could not save club picture: {e}")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred during club picture upload: {e}",
        )


@router.post(
    "/my-club", response_model=club_schemas.Club, status_code=status.HTTP_201_CREATED
)
async def create_my_club(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_user),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    postal_code: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    opening_time: Optional[str] = Form(None),
    closing_time: Optional[str] = Form(None),
    amenities: Optional[str] = Form(None),
    image_file: Optional[UploadFile] = File(None),
):
    """
    Create a new club for the current admin user.
    This endpoint handles multipart/form-data for club creation, including an optional image upload.
    """
    if current_admin.owned_club:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This admin already owns a club.",
        )

    image_url = None
    if image_file:
        # Assuming file_service.upload_file handles the async upload and returns a URL string
        image_url = await file_service.upload_file(image_file, "club_images")

    club_in = club_schemas.ClubCreate(
        name=name,
        description=description,
        address=address,
        city=city,
        postal_code=postal_code,
        phone=phone,
        email=email,
        opening_time=opening_time,
        closing_time=closing_time,
        amenities=amenities,
        image_url=image_url,
        owner_id=current_admin.id,
    )

    return crud.club_crud.create_club(db=db, club=club_in)


@router.get(
    "/club/{club_id}/dashboard-summary", dependencies=[Depends(club_admin_checker())]
)
async def get_dashboard_summary(
    club_id: int,
    db: Session = Depends(get_db),
    summary_date: Optional[date] = Query(None, alias="date"),
):
    """
    Get a summary of dashboard metrics for a specific club.
    """
    target_date = summary_date or datetime.utcnow().date()

    # Get total bookings for the day
    bookings_count = crud.booking_crud.get_bookings_count_by_club_and_date(
        db, club_id=club_id, target_date=target_date
    )

    # Get court occupancy
    courts = crud.court_crud.get_courts_by_club(db, club_id=club_id)
    total_slots = len(courts) * 24  # Assuming 1-hour slots
    occupied_slots = bookings_count
    occupancy_rate = (occupied_slots / total_slots) * 100 if total_slots > 0 else 0

    # Get recent player activity (e.g., last 5 games)
    recent_games = crud.game_crud.get_recent_games_by_club(db, club_id=club_id, limit=5)

    return {
        "total_bookings_today": bookings_count,
        "occupancy_rate_percent": round(occupancy_rate, 2),
        "recent_activity": recent_games,
    }
