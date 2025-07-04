"""Business metrics and analytics schemas."""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class DateRange(BaseModel):
    """Date range for filtering analytics."""
    start_date: date
    end_date: date


class RevenueMetrics(BaseModel):
    """Revenue metrics response."""
    total_revenue: Decimal = Field(..., description="Total revenue for the period")
    booking_revenue: Decimal = Field(..., description="Revenue from bookings")
    tournament_revenue: Decimal = Field(..., description="Revenue from tournaments")
    membership_revenue: Decimal = Field(..., description="Revenue from memberships")
    growth_rate: Optional[float] = Field(
        None, description="Revenue growth rate percentage"
    )
    previous_period_revenue: Optional[Decimal] = Field(
        None, description="Previous period revenue for comparison"
    )


class BookingAnalytics(BaseModel):
    """Booking analytics response."""
    total_bookings: int = Field(..., description="Total number of bookings")
    confirmed_bookings: int = Field(..., description="Number of confirmed bookings")
    cancelled_bookings: int = Field(..., description="Number of cancelled bookings")
    utilization_rate: float = Field(..., description="Court utilization percentage")
    average_duration: float = Field(
        ..., description="Average booking duration in hours"
    )
    peak_hour: Optional[int] = Field(None, description="Most popular booking hour")
    unique_players: int = Field(..., description="Number of unique players")


class TournamentMetrics(BaseModel):
    """Tournament metrics response."""
    active_tournaments: int = Field(..., description="Number of active tournaments")
    completed_tournaments: int = Field(
        ..., description="Number of completed tournaments"
    )
    total_participants: int = Field(..., description="Total tournament participants")
    average_participants_per_tournament: float = Field(
        ..., description="Average participants per tournament"
    )
    tournament_revenue: Decimal = Field(..., description="Total tournament revenue")


class BusinessMetrics(BaseModel):
    """Comprehensive business metrics response."""
    revenue: RevenueMetrics
    bookings: BookingAnalytics
    tournaments: TournamentMetrics
    period: DateRange


class UpcomingBooking(BaseModel):
    """Upcoming booking details."""
    id: int
    court_name: str
    court_id: int
    user_name: str
    user_id: int
    start_time: datetime
    end_time: datetime
    status: str
    has_game: bool = Field(..., description="Whether booking has an associated game")

    class Config:
        from_attributes = True


class TournamentSummary(BaseModel):
    """Tournament summary for dashboard."""
    id: int
    name: str
    status: str
    participants: int
    max_participants: int
    start_date: datetime
    end_date: datetime
    entry_fee: float

    class Config:
        from_attributes = True


class ClubOverview(BaseModel):
    """Multi-club overview metrics."""
    club_id: int
    club_name: str
    today_bookings: int
    monthly_revenue: Decimal
    utilization_rate: float
    active_tournaments: int


class MultiClubMetrics(BaseModel):
    """Aggregated metrics across multiple clubs."""
    clubs: list[ClubOverview]
    total_revenue: Decimal
    total_bookings: int
    average_utilization: float
    total_active_tournaments: int


class DailyAnalytics(BaseModel):
    """Daily analytics data point."""
    date: date
    total_bookings: int
    total_revenue: Decimal
    unique_players: int
    court_utilization_rate: Optional[float]

    class Config:
        from_attributes = True


class RevenueChart(BaseModel):
    """Revenue chart data."""
    dates: list[date]
    daily_revenue: list[Decimal]
    booking_revenue: list[Decimal]
    tournament_revenue: list[Decimal]


class PaymentTransactionCreate(BaseModel):
    """Create payment transaction schema."""
    booking_id: Optional[int] = None
    tournament_id: Optional[int] = None
    user_id: int
    club_id: int
    amount: Decimal
    currency: str = "EUR"
    payment_method: Optional[str] = None
    payment_status: str
    payment_gateway: Optional[str] = None
    gateway_transaction_id: Optional[str] = None
    payment_metadata: Optional[dict] = None


class PaymentTransactionResponse(BaseModel):
    """Payment transaction response schema."""
    id: int
    booking_id: Optional[int]
    tournament_id: Optional[int]
    user_id: int
    club_id: int
    amount: Decimal
    currency: str
    payment_method: Optional[str]
    payment_status: str
    payment_gateway: Optional[str]
    gateway_transaction_id: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    payment_metadata: Optional[dict]

    class Config:
        from_attributes = True
