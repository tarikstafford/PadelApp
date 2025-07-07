"""Add hourly scheduling fields to tournaments

Revision ID: tournament_hourly_scheduling
Revises: 627120000tsafe_tournament_system_safe
Create Date: 2025-01-07 12:00:00.000000

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "tournament_hourly_scheduling"
down_revision = "627120000tsafe_tournament_system_safe"
branch_labels = None
depends_on = None


def upgrade():
    """Add new fields to support hourly tournament scheduling"""
    # Add new columns to tournaments table
    op.add_column("tournaments", sa.Column("auto_schedule_enabled", sa.Boolean(), nullable=False, server_default="true"))
    op.add_column("tournaments", sa.Column("hourly_time_slots", sa.JSON(), nullable=True))
    op.add_column("tournaments", sa.Column("assigned_court_ids", sa.JSON(), nullable=True))
    op.add_column("tournaments", sa.Column("schedule_generated", sa.Boolean(), nullable=False, server_default="false"))


def downgrade():
    """Remove hourly tournament scheduling fields"""
    # Remove columns from tournaments table
    op.drop_column("tournaments", "schedule_generated")
    op.drop_column("tournaments", "assigned_court_ids")
    op.drop_column("tournaments", "hourly_time_slots")
    op.drop_column("tournaments", "auto_schedule_enabled")
