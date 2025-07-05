"""add_financial_tracking_and_analytics_tables

Revision ID: 00762c138e14
Revises: 1b340b777ae2
Create Date: 2025-07-04 15:17:31.248821

"""
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "00762c138e14"
down_revision: Union[str, None] = "1b340b777ae2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create payment transactions table
    op.create_table(
        "payment_transactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("booking_id", sa.Integer(), nullable=True),
        sa.Column("tournament_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("club_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("currency", sa.String(3), server_default="EUR", nullable=False),
        sa.Column("payment_method", sa.String(50), nullable=True),
        sa.Column("payment_status", sa.String(20), nullable=False),
        sa.Column("payment_gateway", sa.String(50), nullable=True),
        sa.Column("gateway_transaction_id", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("payment_metadata", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["booking_id"], ["bookings.id"], ),
        sa.ForeignKeyConstraint(["tournament_id"], ["tournaments.id"], ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ),
        sa.ForeignKeyConstraint(["club_id"], ["clubs.id"], ),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index("ix_payment_transactions_club_created", "payment_transactions", ["club_id", "created_at"])
    op.create_index("ix_payment_transactions_user_id", "payment_transactions", ["user_id"])

    # Create revenue records table
    op.create_table(
        "revenue_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("club_id", sa.Integer(), nullable=False),
        sa.Column("revenue_type", sa.String(50), nullable=False),  # booking, tournament, membership, other
        sa.Column("source_id", sa.Integer(), nullable=True),  # FK to booking_id, tournament_id, etc.
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["club_id"], ["clubs.id"], ),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index("ix_revenue_records_club_date", "revenue_records", ["club_id", "date"])

    # Create club daily analytics table
    op.create_table(
        "club_daily_analytics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("club_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("total_bookings", sa.Integer(), server_default="0", nullable=False),
        sa.Column("total_revenue", sa.Numeric(precision=10, scale=2), server_default="0", nullable=False),
        sa.Column("unique_players", sa.Integer(), server_default="0", nullable=False),
        sa.Column("court_utilization_rate", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("average_booking_duration", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("peak_hour", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["club_id"], ["clubs.id"], ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("club_id", "date")
    )
    op.create_index("ix_club_daily_analytics_club_date", "club_daily_analytics", ["club_id", "date"])

    # Create player analytics table
    op.create_table(
        "player_analytics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("club_id", sa.Integer(), nullable=False),
        sa.Column("month", sa.Date(), nullable=False),
        sa.Column("games_played", sa.Integer(), server_default="0", nullable=False),
        sa.Column("win_rate", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("total_spent", sa.Numeric(precision=10, scale=2), server_default="0", nullable=False),
        sa.Column("favorite_court_id", sa.Integer(), nullable=True),
        sa.Column("favorite_play_time", sa.Integer(), nullable=True),  # hour of day
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ),
        sa.ForeignKeyConstraint(["club_id"], ["clubs.id"], ),
        sa.ForeignKeyConstraint(["favorite_court_id"], ["courts.id"], ),
        sa.PrimaryKeyConstraint("id")
    )

    # Create club memberships table
    op.create_table(
        "club_memberships",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("club_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("membership_type", sa.String(50), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("monthly_fee", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["club_id"], ["clubs.id"], ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index("ix_club_memberships_club_user", "club_memberships", ["club_id", "user_id"])

    # Create club expenses table
    op.create_table(
        "club_expenses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("club_id", sa.Integer(), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["club_id"], ["clubs.id"], ),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index("ix_club_expenses_club_date", "club_expenses", ["club_id", "date"])

    # Create performance indexes for analytics queries
    op.create_index("ix_bookings_club_date", "bookings", ["court_id", "start_time"])
    op.create_index("ix_games_club_date", "games", ["club_id", "start_time"])
    op.create_index("ix_game_players_user_game", "game_players", ["user_id", "game_id"])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index("ix_game_players_user_game", "game_players")
    op.drop_index("ix_games_club_date", "games")
    op.drop_index("ix_bookings_club_date", "bookings")
    op.drop_index("ix_club_expenses_club_date", "club_expenses")
    op.drop_index("ix_club_memberships_club_user", "club_memberships")
    op.drop_index("ix_club_daily_analytics_club_date", "club_daily_analytics")
    op.drop_index("ix_revenue_records_club_date", "revenue_records")
    op.drop_index("ix_payment_transactions_user_id", "payment_transactions")
    op.drop_index("ix_payment_transactions_club_created", "payment_transactions")

    # Drop tables
    op.drop_table("club_expenses")
    op.drop_table("club_memberships")
    op.drop_table("player_analytics")
    op.drop_table("club_daily_analytics")
    op.drop_table("revenue_records")
    op.drop_table("payment_transactions")
