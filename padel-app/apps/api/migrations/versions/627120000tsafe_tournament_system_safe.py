"""Tournament system - safe migration with existence checks

Revision ID: 627120000tsafe
Revises: 5f1f2e2e1e0a
Create Date: 2025-06-27 12:00:00.000000

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "627120000tsafe"
down_revision = "5f1f2e2e1e0a"
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Safe enum creation using DDL
    connection = op.get_bind()

    # Create enums only if they don't exist
    connection.execute(sa.text("""
        DO $$ BEGIN
            CREATE TYPE tournamentstatus AS ENUM ('DRAFT', 'REGISTRATION_OPEN', 'REGISTRATION_CLOSED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """))

    connection.execute(sa.text("""
        DO $$ BEGIN
            CREATE TYPE tournamenttype AS ENUM ('SINGLE_ELIMINATION', 'DOUBLE_ELIMINATION', 'AMERICANO', 'FIXED_AMERICANO');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """))

    connection.execute(sa.text("""
        DO $$ BEGIN
            CREATE TYPE tournamentcategory AS ENUM ('BRONZE', 'SILVER', 'GOLD', 'PLATINUM');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """))

    connection.execute(sa.text("""
        DO $$ BEGIN
            CREATE TYPE matchstatus AS ENUM ('SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', 'WALKOVER');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """))

    # Create tables only if they don't exist
    connection.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS tournaments (
            id SERIAL PRIMARY KEY,
            club_id INTEGER NOT NULL REFERENCES clubs(id),
            name VARCHAR NOT NULL,
            description TEXT,
            tournament_type tournamenttype NOT NULL,
            start_date TIMESTAMP NOT NULL,
            end_date TIMESTAMP NOT NULL,
            registration_deadline TIMESTAMP NOT NULL,
            status tournamentstatus NOT NULL DEFAULT 'DRAFT',
            max_participants INTEGER NOT NULL,
            entry_fee FLOAT,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        );
    """))

    connection.execute(sa.text("""
        CREATE INDEX IF NOT EXISTS ix_tournaments_club_id ON tournaments(club_id);
        CREATE INDEX IF NOT EXISTS ix_tournaments_id ON tournaments(id);
        CREATE INDEX IF NOT EXISTS ix_tournaments_name ON tournaments(name);
    """))

    connection.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS tournament_category_configs (
            id SERIAL PRIMARY KEY,
            tournament_id INTEGER NOT NULL REFERENCES tournaments(id),
            category tournamentcategory NOT NULL,
            max_participants INTEGER NOT NULL,
            min_elo FLOAT NOT NULL,
            max_elo FLOAT NOT NULL
        );
    """))

    connection.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS tournament_teams (
            id SERIAL PRIMARY KEY,
            tournament_id INTEGER NOT NULL REFERENCES tournaments(id),
            category_config_id INTEGER NOT NULL REFERENCES tournament_category_configs(id),
            team_id INTEGER NOT NULL REFERENCES teams(id),
            seed INTEGER,
            average_elo FLOAT NOT NULL,
            registration_date TIMESTAMP NOT NULL DEFAULT NOW(),
            is_active BOOLEAN NOT NULL DEFAULT TRUE
        );
    """))

    connection.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS tournament_matches (
            id SERIAL PRIMARY KEY,
            tournament_id INTEGER NOT NULL REFERENCES tournaments(id),
            category_config_id INTEGER NOT NULL REFERENCES tournament_category_configs(id),
            team1_id INTEGER REFERENCES tournament_teams(id),
            team2_id INTEGER REFERENCES tournament_teams(id),
            round_number INTEGER NOT NULL,
            match_number INTEGER NOT NULL,
            scheduled_time TIMESTAMP,
            court_id INTEGER REFERENCES courts(id),
            status matchstatus NOT NULL DEFAULT 'SCHEDULED',
            winning_team_id INTEGER REFERENCES tournament_teams(id),
            team1_score INTEGER,
            team2_score INTEGER,
            game_id INTEGER REFERENCES games(id),
            winner_advances_to_match_id INTEGER REFERENCES tournament_matches(id),
            loser_advances_to_match_id INTEGER REFERENCES tournament_matches(id),
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        );
    """))

    connection.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS tournament_court_bookings (
            id SERIAL PRIMARY KEY,
            tournament_id INTEGER NOT NULL REFERENCES tournaments(id),
            court_id INTEGER NOT NULL REFERENCES courts(id),
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP NOT NULL,
            is_occupied BOOLEAN NOT NULL DEFAULT FALSE,
            match_id INTEGER REFERENCES tournament_matches(id),
            created_at TIMESTAMP NOT NULL DEFAULT NOW()
        );
    """))

    connection.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS tournament_trophies (
            id SERIAL PRIMARY KEY,
            tournament_id INTEGER NOT NULL REFERENCES tournaments(id),
            category_config_id INTEGER NOT NULL REFERENCES tournament_category_configs(id),
            user_id INTEGER NOT NULL REFERENCES users(id),
            team_id INTEGER NOT NULL REFERENCES teams(id),
            position INTEGER NOT NULL,
            trophy_type VARCHAR NOT NULL,
            awarded_at TIMESTAMP NOT NULL DEFAULT NOW()
        );
    """))

def downgrade() -> None:
    # Drop tables in reverse order (only if they exist)
    op.drop_table("tournament_trophies", if_exists=True)
    op.drop_table("tournament_court_bookings", if_exists=True)
    op.drop_table("tournament_matches", if_exists=True)
    op.drop_table("tournament_teams", if_exists=True)
    op.drop_table("tournament_category_configs", if_exists=True)
    op.drop_table("tournaments", if_exists=True)

    # Drop enum types (PostgreSQL will automatically handle dependencies)
    connection = op.get_bind()
    connection.execute(sa.text("DROP TYPE IF EXISTS matchstatus"))
    connection.execute(sa.text("DROP TYPE IF EXISTS tournamentcategory"))
    connection.execute(sa.text("DROP TYPE IF EXISTS tournamenttype"))
    connection.execute(sa.text("DROP TYPE IF EXISTS tournamentstatus"))
