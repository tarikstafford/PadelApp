"""Add recurring tournament support

Revision ID: add_recurring_tournaments
Revises: 627120000tsafe
Create Date: 2025-07-07 12:00:00.000000

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "add_recurring_tournaments"
down_revision = "627120000tsafe"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Safe enum creation using DDL
    connection = op.get_bind()

    # Create recurrence pattern enum
    connection.execute(sa.text("""
        DO $$ BEGIN
            CREATE TYPE recurrencepattern AS ENUM ('WEEKLY', 'MONTHLY', 'CUSTOM');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """))

    # Create recurring_tournaments table
    connection.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS recurring_tournaments (
            id SERIAL PRIMARY KEY,
            club_id INTEGER NOT NULL REFERENCES clubs(id),
            series_name VARCHAR NOT NULL,
            description TEXT,
            recurrence_pattern recurrencepattern NOT NULL,
            interval_value INTEGER NOT NULL DEFAULT 1,
            days_of_week JSON,
            day_of_month INTEGER,
            series_start_date TIMESTAMP NOT NULL,
            series_end_date TIMESTAMP,
            tournament_type tournamenttype NOT NULL,
            duration_hours INTEGER NOT NULL DEFAULT 3,
            registration_deadline_hours INTEGER NOT NULL DEFAULT 24,
            max_participants INTEGER NOT NULL,
            entry_fee FLOAT DEFAULT 0.0,
            advance_generation_days INTEGER NOT NULL DEFAULT 30,
            auto_generation_enabled BOOLEAN NOT NULL DEFAULT TRUE,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        );
    """))

    # Create indexes for recurring_tournaments
    connection.execute(sa.text("""
        CREATE INDEX IF NOT EXISTS ix_recurring_tournaments_id ON recurring_tournaments(id);
        CREATE INDEX IF NOT EXISTS ix_recurring_tournaments_club_id ON recurring_tournaments(club_id);
        CREATE INDEX IF NOT EXISTS ix_recurring_tournaments_series_name ON recurring_tournaments(series_name);
    """))

    # Create recurring_tournament_category_templates table
    connection.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS recurring_tournament_category_templates (
            id SERIAL PRIMARY KEY,
            recurring_tournament_id INTEGER NOT NULL REFERENCES recurring_tournaments(id),
            category tournamentcategory NOT NULL,
            max_participants INTEGER NOT NULL,
            min_elo FLOAT NOT NULL,
            max_elo FLOAT NOT NULL
        );
    """))

    # Add recurring_tournament_id to tournaments table
    connection.execute(sa.text("""
        ALTER TABLE tournaments
        ADD COLUMN IF NOT EXISTS recurring_tournament_id INTEGER REFERENCES recurring_tournaments(id);
    """))

    # Create index for the new foreign key
    connection.execute(sa.text("""
        CREATE INDEX IF NOT EXISTS ix_tournaments_recurring_tournament_id
        ON tournaments(recurring_tournament_id);
    """))


def downgrade() -> None:
    # Drop the new column from tournaments table
    connection = op.get_bind()
    connection.execute(sa.text("ALTER TABLE tournaments DROP COLUMN IF EXISTS recurring_tournament_id"))

    # Drop tables in reverse order
    op.drop_table("recurring_tournament_category_templates", if_exists=True)
    op.drop_table("recurring_tournaments", if_exists=True)

    # Drop enum type
    connection.execute(sa.text("DROP TYPE IF EXISTS recurrencepattern"))
