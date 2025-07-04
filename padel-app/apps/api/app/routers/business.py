"""Business metrics and analytics API endpoints."""
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.core.security import get_current_active_user
from app.crud.business_crud import BusinessCRUD
from app.middleware.auth import role_checker
from app.models import User, UserRole
from app.schemas.business_schemas import (
    BusinessMetrics,
    DateRange,
    MultiClubMetrics,
    TournamentSummary,
    UpcomingBooking,
)

router = APIRouter(prefix="/business", tags=["business"])


@router.get("/club/{club_id}/metrics", response_model=BusinessMetrics)
async def get_club_business_metrics(
    club_id: int,
    start_date: date = Query(..., description="Start date for metrics"),
    end_date: date = Query(..., description="End date for metrics"),
    db: Session = Depends(get_db),
    current_user: User = Depends(role_checker([UserRole.CLUB_ADMIN, UserRole.SUPER_ADMIN])),
):
    """Get comprehensive business metrics for a club."""
    # TODO: Add club admin permission check

    date_range = DateRange(start_date=start_date, end_date=end_date)

    try:
        metrics = BusinessCRUD.get_business_metrics(db, club_id, date_range)
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get business metrics: {e!s}")


@router.get("/club/{club_id}/upcoming-bookings", response_model=list[UpcomingBooking])
async def get_upcoming_bookings(
    club_id: int,
    days_ahead: int = Query(7, description="Number of days to look ahead"),
    db: Session = Depends(get_db),
    current_user: User = Depends(role_checker([UserRole.CLUB_ADMIN, UserRole.SUPER_ADMIN])),
):
    """Get upcoming bookings for a club."""
    # TODO: Add club admin permission check

    try:
        bookings = BusinessCRUD.get_upcoming_bookings(db, club_id, days_ahead)

        upcoming_bookings = []
        for booking in bookings:
            upcoming_bookings.append(
                UpcomingBooking(
                    id=booking.id,
                    court_name=booking.court.name,
                    court_id=booking.court_id,
                    user_name=booking.user.full_name,
                    user_id=booking.user_id,
                    start_time=booking.start_time,
                    end_time=booking.end_time,
                    status=booking.status.value,
                    has_game=booking.game is not None,
                )
            )

        return upcoming_bookings
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get upcoming bookings: {e!s}")


@router.get("/club/{club_id}/tournaments/active", response_model=list[TournamentSummary])
async def get_active_tournaments(
    club_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_checker([UserRole.CLUB_ADMIN, UserRole.SUPER_ADMIN])),
):
    """Get active tournaments for a club."""
    # TODO: Add club admin permission check

    try:
        tournaments = BusinessCRUD.get_active_tournaments(db, club_id)

        tournament_summaries = []
        for tournament in tournaments:
            # TODO: Get actual participant count from tournament teams
            participants = 0

            tournament_summaries.append(
                TournamentSummary(
                    id=tournament.id,
                    name=tournament.name,
                    status=tournament.status.value,
                    participants=participants,
                    max_participants=tournament.max_participants,
                    start_date=tournament.start_date,
                    end_date=tournament.end_date,
                    entry_fee=tournament.entry_fee or 0.0,
                )
            )

        return tournament_summaries
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get active tournaments: {e!s}")


@router.get("/my-clubs", response_model=list[dict])
async def get_my_clubs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get all clubs that the current user administers."""
    try:
        clubs = BusinessCRUD.get_user_administered_clubs(db, current_user.id)

        club_list = []
        for club in clubs:
            club_list.append({
                "id": club.id,
                "name": club.name,
                "address": club.address,
                "city": club.city,
                "image_url": club.image_url,
            })

        return club_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get clubs: {e!s}")


@router.get("/multi-club/overview", response_model=MultiClubMetrics)
async def get_multi_club_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(role_checker([UserRole.CLUB_ADMIN, UserRole.SUPER_ADMIN])),
):
    """Get overview metrics across all clubs that the user administers."""
    try:
        clubs = BusinessCRUD.get_user_administered_clubs(db, current_user.id)

        if not clubs:
            return MultiClubMetrics(
                clubs=[],
                total_revenue=0,
                total_bookings=0,
                average_utilization=0,
                total_active_tournaments=0,
            )

        today = date.today()
        month_start = today.replace(day=1)
        date_range = DateRange(start_date=month_start, end_date=today)

        club_overviews = []
        total_revenue = 0
        total_bookings = 0
        total_utilization = 0
        total_active_tournaments = 0

        for club in clubs:
            # Get metrics for each club
            metrics = BusinessCRUD.get_business_metrics(db, club.id, date_range)
            active_tournaments = BusinessCRUD.get_active_tournaments(db, club.id)

            club_overview = {
                "club_id": club.id,
                "club_name": club.name,
                "today_bookings": metrics.bookings.total_bookings,
                "monthly_revenue": metrics.revenue.total_revenue,
                "utilization_rate": metrics.bookings.utilization_rate,
                "active_tournaments": len(active_tournaments),
            }

            club_overviews.append(club_overview)
            total_revenue += metrics.revenue.total_revenue
            total_bookings += metrics.bookings.total_bookings
            total_utilization += metrics.bookings.utilization_rate
            total_active_tournaments += len(active_tournaments)

        average_utilization = total_utilization / len(clubs) if clubs else 0

        return MultiClubMetrics(
            clubs=club_overviews,
            total_revenue=total_revenue,
            total_bookings=total_bookings,
            average_utilization=average_utilization,
            total_active_tournaments=total_active_tournaments,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get multi-club overview: {e!s}")


@router.get("/club/{club_id}/revenue-chart")
async def get_revenue_chart_data(
    club_id: int,
    days: int = Query(30, description="Number of days for chart data"),
    db: Session = Depends(get_db),
    current_user: User = Depends(role_checker([UserRole.CLUB_ADMIN, UserRole.SUPER_ADMIN])),
):
    """Get revenue chart data for a club."""
    # TODO: Add club admin permission check

    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        date_range = DateRange(start_date=start_date, end_date=end_date)

        daily_analytics = BusinessCRUD.get_daily_analytics(db, club_id, date_range)

        # Create chart data
        chart_data = {
            "dates": [],
            "daily_revenue": [],
            "booking_revenue": [],
            "tournament_revenue": [],
        }

        for analytics in daily_analytics:
            chart_data["dates"].append(analytics.date)
            chart_data["daily_revenue"].append(float(analytics.total_revenue))
            # TODO: Break down by revenue type
            chart_data["booking_revenue"].append(float(analytics.total_revenue * 0.8))  # Mock data
            chart_data["tournament_revenue"].append(float(analytics.total_revenue * 0.2))  # Mock data

        return chart_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get revenue chart data: {e!s}")


@router.get("/club/{club_id}/dashboard-summary")
async def get_enhanced_dashboard_summary(
    club_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_checker([UserRole.CLUB_ADMIN, UserRole.SUPER_ADMIN])),
):
    """Get enhanced dashboard summary for a club."""
    # TODO: Add club admin permission check

    try:
        today = date.today()
        week_start = today - timedelta(days=7)
        date_range = DateRange(start_date=week_start, end_date=today)

        # Get comprehensive metrics
        metrics = BusinessCRUD.get_business_metrics(db, club_id, date_range)
        upcoming_bookings = BusinessCRUD.get_upcoming_bookings(db, club_id, 7)
        active_tournaments = BusinessCRUD.get_active_tournaments(db, club_id)

        return {
            "revenue_metrics": {
                "weekly_revenue": float(metrics.revenue.total_revenue),
                "growth_rate": metrics.revenue.growth_rate,
                "booking_revenue": float(metrics.revenue.booking_revenue),
                "tournament_revenue": float(metrics.revenue.tournament_revenue),
            },
            "booking_metrics": {
                "total_bookings": metrics.bookings.total_bookings,
                "utilization_rate": metrics.bookings.utilization_rate,
                "unique_players": metrics.bookings.unique_players,
                "upcoming_count": len(upcoming_bookings),
            },
            "tournament_metrics": {
                "active_tournaments": len(active_tournaments),
                "completed_tournaments": metrics.tournaments.completed_tournaments,
                "tournament_revenue": float(metrics.tournaments.tournament_revenue),
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard summary: {e!s}")
