"""Add notification and score management models - RAW SQL VERSION

Revision ID: rawsql_abc123456789
Revises: 00762c138e14
Create Date: 2025-01-05 12:00:00.000000

"""
from collections.abc import Sequence
from typing import Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "abc123456789"
down_revision: Union[str, None] = "00762c138e14"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Use raw SQL to avoid SQLAlchemy automatic ENUM creation

    # Create ENUMs if they don't exist
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE notificationtype AS ENUM (
                'GAME_STARTING', 'GAME_ENDED', 'GAME_CANCELLED',
                'SCORE_SUBMITTED', 'SCORE_CONFIRMED', 'SCORE_DISPUTED',
                'TEAM_INVITATION', 'TOURNAMENT_REGISTRATION',
                'TOURNAMENT_MATCH', 'SYSTEM_ANNOUNCEMENT'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    op.execute("""
        DO $$ BEGIN
            CREATE TYPE notificationpriority AS ENUM ('LOW', 'MEDIUM', 'HIGH', 'URGENT');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    op.execute("""
        DO $$ BEGIN
            CREATE TYPE scorestatus AS ENUM ('PENDING', 'CONFIRMED', 'DISPUTED', 'RESOLVED');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    op.execute("""
        DO $$ BEGIN
            CREATE TYPE confirmationaction AS ENUM ('CONFIRM', 'COUNTER');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    # Create notifications table if it doesn't exist
    op.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            type notificationtype NOT NULL,
            title VARCHAR NOT NULL,
            message TEXT NOT NULL,
            read BOOLEAN NOT NULL DEFAULT false,
            priority notificationpriority NOT NULL DEFAULT 'MEDIUM',
            data JSONB,
            action_url VARCHAR(500),
            action_text VARCHAR(100),
            expires_at TIMESTAMP,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            read_at TIMESTAMP
        );
    """)

    # Handle existing table: rename metadata column to data if it exists
    op.execute("""
        DO $$ BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.columns
                      WHERE table_name = 'notifications' AND column_name = 'metadata') THEN
                ALTER TABLE notifications RENAME COLUMN metadata TO data;
            END IF;
        END $$;
    """)

    # Add missing columns if they don't exist
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                          WHERE table_name = 'notifications' AND column_name = 'action_url') THEN
                ALTER TABLE notifications ADD COLUMN action_url VARCHAR(500);
            END IF;
        END $$;
    """)

    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                          WHERE table_name = 'notifications' AND column_name = 'action_text') THEN
                ALTER TABLE notifications ADD COLUMN action_text VARCHAR(100);
            END IF;
        END $$;
    """)

    # Create indexes if they don't exist
    op.execute("CREATE INDEX IF NOT EXISTS ix_notifications_user_id ON notifications(user_id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_notifications_type ON notifications(type);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_notifications_read ON notifications(read);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_notifications_created_at ON notifications(created_at);")

    # Create notification_preferences table if it doesn't exist
    op.execute("""
        CREATE TABLE IF NOT EXISTS notification_preferences (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            game_starting_enabled BOOLEAN NOT NULL DEFAULT true,
            game_ended_enabled BOOLEAN NOT NULL DEFAULT true,
            score_notifications_enabled BOOLEAN NOT NULL DEFAULT true,
            team_invitations_enabled BOOLEAN NOT NULL DEFAULT true,
            game_invitations_enabled BOOLEAN NOT NULL DEFAULT true,
            tournament_reminders_enabled BOOLEAN NOT NULL DEFAULT true,
            elo_updates_enabled BOOLEAN NOT NULL DEFAULT true,
            general_notifications_enabled BOOLEAN NOT NULL DEFAULT true,
            game_reminder_minutes INTEGER NOT NULL DEFAULT 30,
            email_notifications_enabled BOOLEAN NOT NULL DEFAULT false,
            push_notifications_enabled BOOLEAN NOT NULL DEFAULT true,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)

    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_notification_preferences_user_id ON notification_preferences(user_id);")

    # Handle existing notification_preferences table: rename columns to match model
    op.execute("""
        DO $$ BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.columns
                      WHERE table_name = 'notification_preferences' AND column_name = 'game_starting_notifications') THEN
                ALTER TABLE notification_preferences RENAME COLUMN game_starting_notifications TO game_starting_enabled;
            END IF;
        END $$;
    """)

    op.execute("""
        DO $$ BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.columns
                      WHERE table_name = 'notification_preferences' AND column_name = 'game_ended_notifications') THEN
                ALTER TABLE notification_preferences RENAME COLUMN game_ended_notifications TO game_ended_enabled;
            END IF;
        END $$;
    """)

    op.execute("""
        DO $$ BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.columns
                      WHERE table_name = 'notification_preferences' AND column_name = 'score_notifications') THEN
                ALTER TABLE notification_preferences RENAME COLUMN score_notifications TO score_notifications_enabled;
            END IF;
        END $$;
    """)

    op.execute("""
        DO $$ BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.columns
                      WHERE table_name = 'notification_preferences' AND column_name = 'team_notifications') THEN
                ALTER TABLE notification_preferences RENAME COLUMN team_notifications TO team_invitations_enabled;
            END IF;
        END $$;
    """)

    op.execute("""
        DO $$ BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.columns
                      WHERE table_name = 'notification_preferences' AND column_name = 'tournament_notifications') THEN
                ALTER TABLE notification_preferences RENAME COLUMN tournament_notifications TO tournament_reminders_enabled;
            END IF;
        END $$;
    """)

    op.execute("""
        DO $$ BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.columns
                      WHERE table_name = 'notification_preferences' AND column_name = 'system_notifications') THEN
                ALTER TABLE notification_preferences RENAME COLUMN system_notifications TO general_notifications_enabled;
            END IF;
        END $$;
    """)

    op.execute("""
        DO $$ BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.columns
                      WHERE table_name = 'notification_preferences' AND column_name = 'email_notifications') THEN
                ALTER TABLE notification_preferences RENAME COLUMN email_notifications TO email_notifications_enabled;
            END IF;
        END $$;
    """)

    op.execute("""
        DO $$ BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.columns
                      WHERE table_name = 'notification_preferences' AND column_name = 'push_notifications') THEN
                ALTER TABLE notification_preferences RENAME COLUMN push_notifications TO push_notifications_enabled;
            END IF;
        END $$;
    """)

    # Add missing columns if they don't exist
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                          WHERE table_name = 'notification_preferences' AND column_name = 'game_invitations_enabled') THEN
                ALTER TABLE notification_preferences ADD COLUMN game_invitations_enabled BOOLEAN NOT NULL DEFAULT true;
            END IF;
        END $$;
    """)

    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                          WHERE table_name = 'notification_preferences' AND column_name = 'elo_updates_enabled') THEN
                ALTER TABLE notification_preferences ADD COLUMN elo_updates_enabled BOOLEAN NOT NULL DEFAULT true;
            END IF;
        END $$;
    """)

    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                          WHERE table_name = 'notification_preferences' AND column_name = 'game_reminder_minutes') THEN
                ALTER TABLE notification_preferences ADD COLUMN game_reminder_minutes INTEGER NOT NULL DEFAULT 30;
            END IF;
        END $$;
    """)

    # Create game_scores table if it doesn't exist
    op.execute("""
        CREATE TABLE IF NOT EXISTS game_scores (
            id SERIAL PRIMARY KEY,
            game_id INTEGER NOT NULL REFERENCES games(id),
            team1_score INTEGER NOT NULL,
            team2_score INTEGER NOT NULL,
            submitted_by_team INTEGER NOT NULL,
            submitted_by_user_id INTEGER NOT NULL REFERENCES users(id),
            submitted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            status scorestatus NOT NULL DEFAULT 'PENDING',
            final_team1_score INTEGER,
            final_team2_score INTEGER,
            confirmed_at TIMESTAMP,
            admin_resolved BOOLEAN NOT NULL DEFAULT false,
            admin_notes TEXT
        );
    """)

    op.execute("CREATE INDEX IF NOT EXISTS ix_game_scores_game_id ON game_scores(game_id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_game_scores_status ON game_scores(status);")

    # Create score_confirmations table if it doesn't exist
    op.execute("""
        CREATE TABLE IF NOT EXISTS score_confirmations (
            id SERIAL PRIMARY KEY,
            game_score_id INTEGER NOT NULL REFERENCES game_scores(id),
            confirming_team INTEGER NOT NULL,
            confirming_user_id INTEGER NOT NULL REFERENCES users(id),
            action confirmationaction NOT NULL,
            confirmed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            counter_team1_score INTEGER,
            counter_team2_score INTEGER,
            counter_notes TEXT
        );
    """)

    op.execute("CREATE INDEX IF NOT EXISTS ix_score_confirmations_game_score_id ON score_confirmations(game_score_id);")

    # Create team_stats table if it doesn't exist
    op.execute("""
        CREATE TABLE IF NOT EXISTS team_stats (
            id SERIAL PRIMARY KEY,
            team_id INTEGER NOT NULL REFERENCES teams(id),
            games_played INTEGER NOT NULL DEFAULT 0,
            games_won INTEGER NOT NULL DEFAULT 0,
            games_lost INTEGER NOT NULL DEFAULT 0,
            total_points_scored INTEGER NOT NULL DEFAULT 0,
            total_points_conceded INTEGER NOT NULL DEFAULT 0,
            current_average_elo FLOAT,
            peak_average_elo FLOAT,
            lowest_average_elo FLOAT,
            tournaments_participated INTEGER NOT NULL DEFAULT 0,
            tournaments_won INTEGER NOT NULL DEFAULT 0,
            tournament_matches_won INTEGER NOT NULL DEFAULT 0,
            tournament_matches_lost INTEGER NOT NULL DEFAULT 0,
            current_win_streak INTEGER NOT NULL DEFAULT 0,
            current_loss_streak INTEGER NOT NULL DEFAULT 0,
            longest_win_streak INTEGER NOT NULL DEFAULT 0,
            longest_loss_streak INTEGER NOT NULL DEFAULT 0,
            last_game_date TIMESTAMP,
            last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)

    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_team_stats_team_id ON team_stats(team_id);")

    # Create team_game_history table if it doesn't exist
    op.execute("""
        CREATE TABLE IF NOT EXISTS team_game_history (
            id SERIAL PRIMARY KEY,
            team_id INTEGER NOT NULL REFERENCES teams(id),
            game_id INTEGER NOT NULL REFERENCES games(id),
            won INTEGER NOT NULL,
            points_scored INTEGER NOT NULL,
            points_conceded INTEGER NOT NULL,
            opponent_team_id INTEGER REFERENCES teams(id),
            elo_before FLOAT,
            elo_after FLOAT,
            elo_change FLOAT,
            game_date TIMESTAMP NOT NULL,
            is_tournament_game INTEGER NOT NULL DEFAULT 0,
            tournament_id INTEGER REFERENCES tournaments(id),
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)

    op.execute("CREATE INDEX IF NOT EXISTS ix_team_game_history_team_id ON team_game_history(team_id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_team_game_history_game_id ON team_game_history(game_id);")


def downgrade() -> None:
    # Drop tables if they exist
    op.execute("DROP TABLE IF EXISTS team_game_history CASCADE;")
    op.execute("DROP TABLE IF EXISTS team_stats CASCADE;")
    op.execute("DROP TABLE IF EXISTS score_confirmations CASCADE;")
    op.execute("DROP TABLE IF EXISTS game_scores CASCADE;")
    op.execute("DROP TABLE IF EXISTS notification_preferences CASCADE;")
    op.execute("DROP TABLE IF EXISTS notifications CASCADE;")

    # Drop enums if they exist and are not being used
    op.execute("DROP TYPE IF EXISTS confirmationaction;")
    op.execute("DROP TYPE IF EXISTS scorestatus;")
    op.execute("DROP TYPE IF EXISTS notificationpriority;")
    op.execute("DROP TYPE IF EXISTS notificationtype;")
