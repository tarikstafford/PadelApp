"""Add tournament enhancements: recurring tournaments, participant tracking, hourly scheduling - SAFE VERSION

Revision ID: add_tournament_enhancements_safe
Revises: 627120000tsafe
Create Date: 2025-01-07 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_tournament_enhancements_safe'
down_revision = '627120000tsafe'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Get connection for safe DDL operations
    connection = op.get_bind()
    
    # Create recurrence pattern enum only if it doesn't exist
    connection.execute(sa.text("""
        DO $$ BEGIN
            CREATE TYPE recurrencepattern AS ENUM ('WEEKLY', 'MONTHLY', 'CUSTOM');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """))

    # Create recurring_tournaments table only if it doesn't exist
    connection.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS recurring_tournaments (
            id SERIAL PRIMARY KEY,
            club_id INTEGER NOT NULL REFERENCES clubs(id),
            series_name VARCHAR NOT NULL,
            recurrence_pattern recurrencepattern NOT NULL,
            days_of_week INTEGER[],
            day_of_month INTEGER,
            interval_value INTEGER NOT NULL DEFAULT 1,
            series_start_date DATE NOT NULL,
            series_end_date DATE,
            tournament_type tournamenttype NOT NULL,
            template_name VARCHAR NOT NULL,
            template_description TEXT,
            entry_fee FLOAT,
            auto_generation_enabled BOOLEAN NOT NULL DEFAULT TRUE,
            generate_days_ahead INTEGER NOT NULL DEFAULT 30,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        );
    """))

    # Create indexes for recurring_tournaments
    connection.execute(sa.text("""
        CREATE INDEX IF NOT EXISTS ix_recurring_tournaments_club_id ON recurring_tournaments(club_id);
        CREATE INDEX IF NOT EXISTS ix_recurring_tournaments_id ON recurring_tournaments(id);
    """))

    # Create recurring_tournament_category_templates table only if it doesn't exist
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

    # Create index for category templates
    connection.execute(sa.text("""
        CREATE INDEX IF NOT EXISTS ix_recurring_tournament_category_templates_recurring_tournament_id 
        ON recurring_tournament_category_templates(recurring_tournament_id);
    """))

    # Create tournament_participants table only if it doesn't exist
    connection.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS tournament_participants (
            id SERIAL PRIMARY KEY,
            tournament_id INTEGER NOT NULL REFERENCES tournaments(id),
            category_config_id INTEGER NOT NULL REFERENCES tournament_category_configs(id),
            user_id INTEGER NOT NULL REFERENCES users(id),
            elo_at_registration FLOAT NOT NULL,
            seed_position INTEGER,
            match_teams JSONB,
            registration_date TIMESTAMP NOT NULL DEFAULT NOW(),
            is_active BOOLEAN NOT NULL DEFAULT TRUE
        );
    """))

    # Create indexes and unique constraint for tournament_participants
    connection.execute(sa.text("""
        CREATE INDEX IF NOT EXISTS ix_tournament_participants_tournament_id ON tournament_participants(tournament_id);
        CREATE INDEX IF NOT EXISTS ix_tournament_participants_user_id ON tournament_participants(user_id);
    """))
    
    # Add unique constraint safely
    connection.execute(sa.text("""
        DO $$ BEGIN
            ALTER TABLE tournament_participants 
            ADD CONSTRAINT unique_participant_per_tournament 
            UNIQUE (tournament_id, user_id);
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """))

    # Add new columns to tournaments table safely
    connection.execute(sa.text("""
        DO $$ BEGIN
            ALTER TABLE tournaments ADD COLUMN recurring_tournament_id INTEGER REFERENCES recurring_tournaments(id);
        EXCEPTION
            WHEN duplicate_column THEN null;
        END $$;
    """))
    
    connection.execute(sa.text("""
        DO $$ BEGIN
            ALTER TABLE tournaments ADD COLUMN auto_schedule_enabled BOOLEAN DEFAULT FALSE;
        EXCEPTION
            WHEN duplicate_column THEN null;
        END $$;
    """))
    
    connection.execute(sa.text("""
        DO $$ BEGIN
            ALTER TABLE tournaments ADD COLUMN hourly_time_slots JSONB;
        EXCEPTION
            WHEN duplicate_column THEN null;
        END $$;
    """))
    
    connection.execute(sa.text("""
        DO $$ BEGIN
            ALTER TABLE tournaments ADD COLUMN assigned_court_ids JSONB;
        EXCEPTION
            WHEN duplicate_column THEN null;
        END $$;
    """))
    
    connection.execute(sa.text("""
        DO $$ BEGIN
            ALTER TABLE tournaments ADD COLUMN schedule_generated BOOLEAN DEFAULT FALSE;
        EXCEPTION
            WHEN duplicate_column THEN null;
        END $$;
    """))


def downgrade() -> None:
    # Remove columns from tournaments table
    op.drop_column('tournaments', 'schedule_generated')
    op.drop_column('tournaments', 'assigned_court_ids')
    op.drop_column('tournaments', 'hourly_time_slots')
    op.drop_column('tournaments', 'auto_schedule_enabled')
    op.drop_column('tournaments', 'recurring_tournament_id')
    
    # Drop tables in reverse order
    op.drop_table('tournament_participants')
    op.drop_table('recurring_tournament_category_templates')
    op.drop_table('recurring_tournaments')
    
    # Drop enum
    connection = op.get_bind()
    connection.execute(sa.text("DROP TYPE IF EXISTS recurrencepattern"))