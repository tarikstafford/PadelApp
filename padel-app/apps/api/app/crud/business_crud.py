"""CRUD operations for business metrics and analytics."""
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Optional

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.models import (
    Booking,
    BookingStatus,
    Club,
    ClubDailyAnalytics,
    Court,
    PaymentTransaction,
    RevenueRecord,
    Tournament,
    TournamentStatus,
    User,
)
from app.schemas.business_schemas import (
    BookingAnalytics,
    BusinessMetrics,
    DateRange,
    PaymentTransactionCreate,
    RevenueMetrics,
    TournamentMetrics,
)


class BusinessCRUD:
    """CRUD operations for business metrics."""

    @staticmethod
    def get_revenue_metrics(
        db: Session, club_id: int, date_range: DateRange
    ) -> RevenueMetrics:
        """Get revenue metrics for a club within a date range."""
        # Current period revenue
        current_revenue = db.query(func.sum(RevenueRecord.amount)).filter(
            and_(
                RevenueRecord.club_id == club_id,
                RevenueRecord.date >= date_range.start_date,
                RevenueRecord.date <= date_range.end_date,
            )
        ).scalar() or Decimal("0")

        # Revenue by type
        revenue_by_type = (
            db.query(
                RevenueRecord.revenue_type,
                func.sum(RevenueRecord.amount).label("total"),
            )
            .filter(
                and_(
                    RevenueRecord.club_id == club_id,
                    RevenueRecord.date >= date_range.start_date,
                    RevenueRecord.date <= date_range.end_date,
                )
            )
            .group_by(RevenueRecord.revenue_type)
            .all()
        )

        revenue_dict = {r.revenue_type: r.total for r in revenue_by_type}

        # Previous period for growth calculation
        period_days = (date_range.end_date - date_range.start_date).days
        prev_start = date_range.start_date - timedelta(days=period_days)
        prev_end = date_range.start_date - timedelta(days=1)

        previous_revenue = db.query(func.sum(RevenueRecord.amount)).filter(
            and_(
                RevenueRecord.club_id == club_id,
                RevenueRecord.date >= prev_start,
                RevenueRecord.date <= prev_end,
            )
        ).scalar() or Decimal("0")

        # Calculate growth rate
        growth_rate = None
        if previous_revenue > 0:
            growth_rate = float(
                ((current_revenue - previous_revenue) / previous_revenue) * 100
            )

        return RevenueMetrics(
            total_revenue=current_revenue,
            booking_revenue=revenue_dict.get("booking", Decimal("0")),
            tournament_revenue=revenue_dict.get("tournament", Decimal("0")),
            membership_revenue=revenue_dict.get("membership", Decimal("0")),
            growth_rate=growth_rate,
            previous_period_revenue=previous_revenue,
        )

    @staticmethod
    def get_booking_analytics(
        db: Session, club_id: int, date_range: DateRange
    ) -> BookingAnalytics:
        """Get booking analytics for a club within a date range."""
        # Get all bookings in the date range
        bookings_query = (
            db.query(Booking)
            .join(Court)
            .filter(
                and_(
                    Court.club_id == club_id,
                    Booking.start_time
                    >= datetime.combine(date_range.start_date, datetime.min.time()),
                    Booking.start_time
                    <= datetime.combine(date_range.end_date, datetime.max.time()),
                )
            )
        )

        total_bookings = bookings_query.count()

        # Bookings by status
        booking_counts = (
            bookings_query.with_entities(
                Booking.status, func.count(Booking.id).label("count")
            )
            .group_by(Booking.status)
            .all()
        )

        status_dict = dict(booking_counts)
        confirmed_bookings = status_dict.get(BookingStatus.CONFIRMED, 0)
        cancelled_bookings = status_dict.get(BookingStatus.CANCELLED, 0)

        # Unique players
        unique_players = (
            bookings_query.with_entities(Booking.user_id).distinct().count()
        )

        # Average duration and peak hour
        completed_bookings = bookings_query.filter(
            Booking.status == BookingStatus.COMPLETED
        ).all()

        total_duration = sum(
            (booking.end_time - booking.start_time).total_seconds() / 3600
            for booking in completed_bookings
        )
        avg_duration = (
            total_duration / len(completed_bookings) if completed_bookings else 0
        )

        # Peak hour calculation
        hours = [booking.start_time.hour for booking in completed_bookings]
        peak_hour = max(set(hours), key=hours.count) if hours else None

        # Court utilization calculation
        club_courts = db.query(Court).filter(Court.club_id == club_id).all()
        total_court_hours = (
            len(club_courts) * 24 * (date_range.end_date - date_range.start_date).days
        )
        utilized_hours = sum(
            (booking.end_time - booking.start_time).total_seconds() / 3600
            for booking in completed_bookings
        )
        utilization_rate = (
            (utilized_hours / total_court_hours * 100) if total_court_hours > 0 else 0
        )

        return BookingAnalytics(
            total_bookings=total_bookings,
            confirmed_bookings=confirmed_bookings,
            cancelled_bookings=cancelled_bookings,
            utilization_rate=utilization_rate,
            average_duration=avg_duration,
            peak_hour=peak_hour,
            unique_players=unique_players,
        )

    @staticmethod
    def get_tournament_metrics(
        db: Session, club_id: int, date_range: DateRange
    ) -> TournamentMetrics:
        """Get tournament metrics for a club within a date range."""
        tournaments_query = db.query(Tournament).filter(
            and_(
                Tournament.club_id == club_id,
                Tournament.start_date
                >= datetime.combine(date_range.start_date, datetime.min.time()),
                Tournament.start_date
                <= datetime.combine(date_range.end_date, datetime.max.time()),
            )
        )

        active_tournaments = tournaments_query.filter(
            Tournament.status.in_(
                [
                    TournamentStatus.REGISTRATION_OPEN,
                    TournamentStatus.IN_PROGRESS,
                ]
            )
        ).count()

        completed_tournaments = tournaments_query.filter(
            Tournament.status == TournamentStatus.COMPLETED
        ).count()

        # Tournament revenue
        tournament_revenue = db.query(func.sum(RevenueRecord.amount)).filter(
            and_(
                RevenueRecord.club_id == club_id,
                RevenueRecord.revenue_type == "tournament",
                RevenueRecord.date >= date_range.start_date,
                RevenueRecord.date <= date_range.end_date,
            )
        ).scalar() or Decimal("0")

        # Total participants (this would need tournament teams implementation)
        total_participants = 0
        avg_participants = 0

        return TournamentMetrics(
            active_tournaments=active_tournaments,
            completed_tournaments=completed_tournaments,
            total_participants=total_participants,
            average_participants_per_tournament=avg_participants,
            tournament_revenue=tournament_revenue,
        )

    @staticmethod
    def get_business_metrics(
        db: Session, club_id: int, date_range: DateRange
    ) -> BusinessMetrics:
        """Get comprehensive business metrics for a club."""
        revenue = BusinessCRUD.get_revenue_metrics(db, club_id, date_range)
        bookings = BusinessCRUD.get_booking_analytics(db, club_id, date_range)
        tournaments = BusinessCRUD.get_tournament_metrics(db, club_id, date_range)

        return BusinessMetrics(
            revenue=revenue,
            bookings=bookings,
            tournaments=tournaments,
            period=date_range,
        )

    @staticmethod
    def get_upcoming_bookings(
        db: Session, club_id: int, days_ahead: int = 7
    ) -> list[Booking]:
        """Get upcoming bookings for a club."""
        start_date = datetime.now()
        end_date = start_date + timedelta(days=days_ahead)

        return (
            db.query(Booking)
            .join(Court)
            .join(User)
            .filter(
                and_(
                    Court.club_id == club_id,
                    Booking.start_time >= start_date,
                    Booking.start_time <= end_date,
                    Booking.status.in_(
                        [BookingStatus.CONFIRMED, BookingStatus.PENDING]
                    ),
                )
            )
            .order_by(Booking.start_time)
            .all()
        )

    @staticmethod
    def get_active_tournaments(db: Session, club_id: int) -> list[Tournament]:
        """Get active tournaments for a club."""
        return (
            db.query(Tournament)
            .filter(
                and_(
                    Tournament.club_id == club_id,
                    Tournament.status.in_(
                        [
                            TournamentStatus.REGISTRATION_OPEN,
                            TournamentStatus.IN_PROGRESS,
                        ]
                    ),
                )
            )
            .order_by(Tournament.start_date)
            .all()
        )

    @staticmethod
    def create_payment_transaction(
        db: Session, payment_data: PaymentTransactionCreate
    ) -> PaymentTransaction:
        """Create a new payment transaction."""
        payment = PaymentTransaction(**payment_data.dict())
        db.add(payment)
        db.commit()
        db.refresh(payment)
        return payment

    @staticmethod
    def create_revenue_record(
        db: Session,
        club_id: int,
        revenue_type: str,
        amount: Decimal,
        date: date,
        source_id: Optional[int] = None,
    ) -> RevenueRecord:
        """Create a revenue record."""
        revenue = RevenueRecord(
            club_id=club_id,
            revenue_type=revenue_type,
            amount=amount,
            date=date,
            source_id=source_id,
        )
        db.add(revenue)
        db.commit()
        db.refresh(revenue)
        return revenue

    @staticmethod
    def get_daily_analytics(
        db: Session, club_id: int, date_range: DateRange
    ) -> list[ClubDailyAnalytics]:
        """Get daily analytics for a club."""
        return (
            db.query(ClubDailyAnalytics)
            .filter(
                and_(
                    ClubDailyAnalytics.club_id == club_id,
                    ClubDailyAnalytics.date >= date_range.start_date,
                    ClubDailyAnalytics.date <= date_range.end_date,
                )
            )
            .order_by(ClubDailyAnalytics.date)
            .all()
        )

    @staticmethod
    def get_user_administered_clubs(db: Session, user_id: int) -> list[Club]:
        """Get all clubs that a user administers."""
        # This will need to be updated based on the club admin relationship
        owned_club = db.query(Club).filter(Club.owner_id == user_id).first()
        return [owned_club] if owned_club else []
