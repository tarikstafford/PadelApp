"""Add notification and score management models - SAFE VERSION

Revision ID: safe_abc123456789
Revises: 00762c138e14
Create Date: 2025-01-05 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'abc123456789'
down_revision: Union[str, None] = '00762c138e14'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Get connection and inspector to check existing objects
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    existing_tables = inspector.get_table_names()
    
    # Create ENUMs only if they don't exist
    try:
        op.execute("CREATE TYPE IF NOT EXISTS notificationtype AS ENUM ('GAME_STARTING', 'GAME_ENDED', 'GAME_CANCELLED', 'SCORE_SUBMITTED', 'SCORE_CONFIRMED', 'SCORE_DISPUTED', 'TEAM_INVITATION', 'TOURNAMENT_REGISTRATION', 'TOURNAMENT_MATCH', 'SYSTEM_ANNOUNCEMENT')")
    except Exception:
        pass  # Type already exists
        
    try:
        op.execute("CREATE TYPE IF NOT EXISTS notificationpriority AS ENUM ('LOW', 'MEDIUM', 'HIGH', 'URGENT')")
    except Exception:
        pass  # Type already exists
        
    try:
        op.execute("CREATE TYPE IF NOT EXISTS scorestatus AS ENUM ('PENDING', 'CONFIRMED', 'DISPUTED', 'RESOLVED')")
    except Exception:
        pass  # Type already exists
        
    try:
        op.execute("CREATE TYPE IF NOT EXISTS confirmationaction AS ENUM ('CONFIRM', 'COUNTER')")
    except Exception:
        pass  # Type already exists

    # Create notifications table
    if 'notifications' not in existing_tables:
        op.create_table('notifications',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('type', sa.Enum('GAME_STARTING', 'GAME_ENDED', 'GAME_CANCELLED', 'SCORE_SUBMITTED', 'SCORE_CONFIRMED', 'SCORE_DISPUTED', 'TEAM_INVITATION', 'TOURNAMENT_REGISTRATION', 'TOURNAMENT_MATCH', 'SYSTEM_ANNOUNCEMENT', name='notificationtype'), nullable=False),
            sa.Column('title', sa.String(), nullable=False),
            sa.Column('message', sa.Text(), nullable=False),
            sa.Column('read', sa.Boolean(), nullable=False, server_default='false'),
            sa.Column('priority', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'URGENT', name='notificationpriority'), nullable=False, server_default='MEDIUM'),
            sa.Column('metadata', sa.JSON(), nullable=True),
            sa.Column('expires_at', sa.DateTime(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.Column('read_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        try:
            op.create_index('ix_notifications_id', 'notifications', ['id'], unique=False)
            op.create_index('ix_notifications_user_id', 'notifications', ['user_id'], unique=False)
            op.create_index('ix_notifications_type', 'notifications', ['type'], unique=False)
            op.create_index('ix_notifications_read', 'notifications', ['read'], unique=False)
            op.create_index('ix_notifications_created_at', 'notifications', ['created_at'], unique=False)
        except Exception:
            pass  # Indexes might already exist

    # Create notification_preferences table
    if 'notification_preferences' not in existing_tables:
        op.create_table('notification_preferences',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('game_starting_notifications', sa.Boolean(), nullable=False, server_default='true'),
            sa.Column('game_ended_notifications', sa.Boolean(), nullable=False, server_default='true'),
            sa.Column('score_notifications', sa.Boolean(), nullable=False, server_default='true'),
            sa.Column('team_notifications', sa.Boolean(), nullable=False, server_default='true'),
            sa.Column('tournament_notifications', sa.Boolean(), nullable=False, server_default='true'),
            sa.Column('system_notifications', sa.Boolean(), nullable=False, server_default='true'),
            sa.Column('email_notifications', sa.Boolean(), nullable=False, server_default='false'),
            sa.Column('push_notifications', sa.Boolean(), nullable=False, server_default='true'),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        try:
            op.create_index('ix_notification_preferences_user_id', 'notification_preferences', ['user_id'], unique=True)
        except Exception:
            pass

    # Create game_scores table
    if 'game_scores' not in existing_tables:
        op.create_table('game_scores',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('game_id', sa.Integer(), nullable=False),
            sa.Column('team1_score', sa.Integer(), nullable=False),
            sa.Column('team2_score', sa.Integer(), nullable=False),
            sa.Column('submitted_by_team', sa.Integer(), nullable=False),
            sa.Column('submitted_by_user_id', sa.Integer(), nullable=False),
            sa.Column('submitted_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.Column('status', sa.Enum('PENDING', 'CONFIRMED', 'DISPUTED', 'RESOLVED', name='scorestatus'), nullable=False, server_default='PENDING'),
            sa.Column('final_team1_score', sa.Integer(), nullable=True),
            sa.Column('final_team2_score', sa.Integer(), nullable=True),
            sa.Column('confirmed_at', sa.DateTime(), nullable=True),
            sa.Column('admin_resolved', sa.Boolean(), nullable=False, server_default='false'),
            sa.Column('admin_notes', sa.Text(), nullable=True),
            sa.ForeignKeyConstraint(['game_id'], ['games.id'], ),
            sa.ForeignKeyConstraint(['submitted_by_user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        try:
            op.create_index('ix_game_scores_id', 'game_scores', ['id'], unique=False)
            op.create_index('ix_game_scores_game_id', 'game_scores', ['game_id'], unique=False)
            op.create_index('ix_game_scores_status', 'game_scores', ['status'], unique=False)
        except Exception:
            pass

    # Create score_confirmations table
    if 'score_confirmations' not in existing_tables:
        op.create_table('score_confirmations',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('game_score_id', sa.Integer(), nullable=False),
            sa.Column('confirming_team', sa.Integer(), nullable=False),
            sa.Column('confirming_user_id', sa.Integer(), nullable=False),
            sa.Column('action', sa.Enum('CONFIRM', 'COUNTER', name='confirmationaction'), nullable=False),
            sa.Column('confirmed_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.Column('counter_team1_score', sa.Integer(), nullable=True),
            sa.Column('counter_team2_score', sa.Integer(), nullable=True),
            sa.Column('counter_notes', sa.Text(), nullable=True),
            sa.ForeignKeyConstraint(['confirming_user_id'], ['users.id'], ),
            sa.ForeignKeyConstraint(['game_score_id'], ['game_scores.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        try:
            op.create_index('ix_score_confirmations_id', 'score_confirmations', ['id'], unique=False)
            op.create_index('ix_score_confirmations_game_score_id', 'score_confirmations', ['game_score_id'], unique=False)
        except Exception:
            pass

    # Create team_stats table  
    if 'team_stats' not in existing_tables:
        op.create_table('team_stats',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('team_id', sa.Integer(), nullable=False),
            sa.Column('games_played', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('games_won', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('games_lost', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('total_points_scored', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('total_points_conceded', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('current_average_elo', sa.Float(), nullable=True),
            sa.Column('peak_average_elo', sa.Float(), nullable=True),
            sa.Column('lowest_average_elo', sa.Float(), nullable=True),
            sa.Column('tournaments_participated', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('tournaments_won', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('tournament_matches_won', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('tournament_matches_lost', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('current_win_streak', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('current_loss_streak', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('longest_win_streak', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('longest_loss_streak', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('last_game_date', sa.DateTime(), nullable=True),
            sa.Column('last_updated', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        try:
            op.create_index('ix_team_stats_team_id', 'team_stats', ['team_id'], unique=True)
        except Exception:
            pass

    # Create team_game_history table
    if 'team_game_history' not in existing_tables:
        op.create_table('team_game_history',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('team_id', sa.Integer(), nullable=False),
            sa.Column('game_id', sa.Integer(), nullable=False),
            sa.Column('won', sa.Integer(), nullable=False),
            sa.Column('points_scored', sa.Integer(), nullable=False),
            sa.Column('points_conceded', sa.Integer(), nullable=False),
            sa.Column('opponent_team_id', sa.Integer(), nullable=True),
            sa.Column('elo_before', sa.Float(), nullable=True),
            sa.Column('elo_after', sa.Float(), nullable=True),
            sa.Column('elo_change', sa.Float(), nullable=True),
            sa.Column('game_date', sa.DateTime(), nullable=False),
            sa.Column('is_tournament_game', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('tournament_id', sa.Integer(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.ForeignKeyConstraint(['game_id'], ['games.id'], ),
            sa.ForeignKeyConstraint(['opponent_team_id'], ['teams.id'], ),
            sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ),
            sa.ForeignKeyConstraint(['tournament_id'], ['tournaments.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        try:
            op.create_index('ix_team_game_history_team_id', 'team_game_history', ['team_id'], unique=False)
            op.create_index('ix_team_game_history_game_id', 'team_game_history', ['game_id'], unique=False)
        except Exception:
            pass


def downgrade() -> None:
    # Drop tables in reverse order of creation (only if they exist)
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    existing_tables = inspector.get_table_names()
    
    if 'team_game_history' in existing_tables:
        op.drop_table('team_game_history')
    if 'team_stats' in existing_tables:
        op.drop_table('team_stats')
    if 'score_confirmations' in existing_tables:
        op.drop_table('score_confirmations')
    if 'game_scores' in existing_tables:
        op.drop_table('game_scores')
    if 'notification_preferences' in existing_tables:
        op.drop_table('notification_preferences')
    if 'notifications' in existing_tables:
        op.drop_table('notifications')
    
    # Drop enums (only if safe to do so)
    try:
        op.execute("DROP TYPE IF EXISTS confirmationaction")
        op.execute("DROP TYPE IF EXISTS scorestatus")
        op.execute("DROP TYPE IF EXISTS notificationpriority")
        op.execute("DROP TYPE IF EXISTS notificationtype")
    except Exception:
        pass  # Types might be in use by other objects