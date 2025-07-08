"""Fix existing tournaments data - populate new fields with defaults

Revision ID: fix_existing_tournaments_data
Revises: add_tournament_enhancements_safe
Create Date: 2025-01-07 16:45:00.000000

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "fix_existing_tournaments_data"
down_revision = "add_tournament_enhancements_safe"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Get connection for data operations
    connection = op.get_bind()

    # Update existing tournaments to set default values for new fields
    # that might be NULL and causing issues

    # Set default values for auto_schedule_enabled
    connection.execute(sa.text("""
        UPDATE tournaments
        SET auto_schedule_enabled = FALSE
        WHERE auto_schedule_enabled IS NULL;
    """))

    # Set default values for schedule_generated
    connection.execute(sa.text("""
        UPDATE tournaments
        SET schedule_generated = FALSE
        WHERE schedule_generated IS NULL;
    """))

    # Set empty JSON arrays for hourly_time_slots where NULL
    connection.execute(sa.text("""
        UPDATE tournaments
        SET hourly_time_slots = '[]'::jsonb
        WHERE hourly_time_slots IS NULL;
    """))

    # Set empty JSON arrays for assigned_court_ids where NULL
    connection.execute(sa.text("""
        UPDATE tournaments
        SET assigned_court_ids = '[]'::jsonb
        WHERE assigned_court_ids IS NULL;
    """))

    # Make sure entry_fee has a default value
    connection.execute(sa.text("""
        UPDATE tournaments
        SET entry_fee = 0.0
        WHERE entry_fee IS NULL;
    """))

    # Now alter the columns to be NOT NULL with defaults (for new records)
    connection.execute(sa.text("""
        ALTER TABLE tournaments
        ALTER COLUMN auto_schedule_enabled SET DEFAULT FALSE,
        ALTER COLUMN auto_schedule_enabled SET NOT NULL;
    """))

    connection.execute(sa.text("""
        ALTER TABLE tournaments
        ALTER COLUMN schedule_generated SET DEFAULT FALSE,
        ALTER COLUMN schedule_generated SET NOT NULL;
    """))

    connection.execute(sa.text("""
        ALTER TABLE tournaments
        ALTER COLUMN entry_fee SET DEFAULT 0.0,
        ALTER COLUMN entry_fee SET NOT NULL;
    """))


def downgrade() -> None:
    # Revert the NOT NULL constraints
    connection = op.get_bind()

    connection.execute(sa.text("""
        ALTER TABLE tournaments
        ALTER COLUMN auto_schedule_enabled DROP NOT NULL,
        ALTER COLUMN auto_schedule_enabled DROP DEFAULT;
    """))

    connection.execute(sa.text("""
        ALTER TABLE tournaments
        ALTER COLUMN schedule_generated DROP NOT NULL,
        ALTER COLUMN schedule_generated DROP DEFAULT;
    """))

    connection.execute(sa.text("""
        ALTER TABLE tournaments
        ALTER COLUMN entry_fee DROP NOT NULL,
        ALTER COLUMN entry_fee DROP DEFAULT;
    """))
