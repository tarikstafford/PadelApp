"""comprehensive_game_management_enhancements

Revision ID: d5c986b34c46
Revises: 5983356438f4
Create Date: 2025-07-10 14:46:01.339357

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import table, column
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = 'd5c986b34c46'
down_revision: Union[str, None] = '5983356438f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema with comprehensive game management enhancements."""
    
    # Get the connection and inspector
    conn = op.get_bind()
    inspector = inspect(conn)
    
    # Helper function to check if column exists
    def column_exists(table_name, column_name):
        try:
            columns = [col['name'] for col in inspector.get_columns(table_name)]
            return column_name in columns
        except Exception:
            return False
    
    # Helper function to check if table exists
    def table_exists(table_name):
        return inspector.has_table(table_name)
    
    # Helper function to check if enum exists
    def enum_exists(enum_name):
        try:
            result = conn.execute(
                sa.text("SELECT 1 FROM pg_type WHERE typname = :name"),
                {"name": enum_name}
            )
            return result.fetchone() is not None
        except Exception:
            return False
    
    # Add onboarding tracking to users table
    if not column_exists('users', 'onboarding_completed'):
        op.add_column('users', sa.Column('onboarding_completed', sa.Boolean(), nullable=False, server_default='false'))
    
    if not column_exists('users', 'onboarding_completed_at'):
        op.add_column('users', sa.Column('onboarding_completed_at', sa.TIMESTAMP(timezone=True), nullable=True))

    # Add privacy settings to users table
    if not column_exists('users', 'is_game_history_public'):
        op.add_column('users', sa.Column('is_game_history_public', sa.Boolean(), nullable=False, server_default='true'))
    
    if not column_exists('users', 'is_game_statistics_public'):
        op.add_column('users', sa.Column('is_game_statistics_public', sa.Boolean(), nullable=False, server_default='true'))

    # Extend teams table for persistence
    if not column_exists('teams', 'description'):
        op.add_column('teams', sa.Column('description', sa.Text(), nullable=True))
    
    if not column_exists('teams', 'logo_url'):
        op.add_column('teams', sa.Column('logo_url', sa.String(), nullable=True))
    
    if not column_exists('teams', 'created_by'):
        op.add_column('teams', sa.Column('created_by', sa.Integer(), nullable=True))
    
    if not column_exists('teams', 'created_at'):
        op.add_column('teams', sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')))
    
    if not column_exists('teams', 'is_active'):
        op.add_column('teams', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))

    # Create team membership role enum
    if not enum_exists('teammembershiprole'):
        conn.execute(sa.text("CREATE TYPE teammembershiprole AS ENUM ('OWNER', 'ADMIN', 'MEMBER')"))

    # Create team membership status enum
    if not enum_exists('teammembershipstatus'):
        conn.execute(sa.text("CREATE TYPE teammembershipstatus AS ENUM ('ACTIVE', 'INACTIVE', 'PENDING', 'REMOVED')"))

    # Create team_memberships table
    if not table_exists('team_memberships'):
        op.create_table('team_memberships',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('team_id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('role', postgresql.ENUM('OWNER', 'ADMIN', 'MEMBER', name='teammembershiprole', create_type=False), nullable=False, server_default='MEMBER'),
            sa.Column('status', postgresql.ENUM('ACTIVE', 'INACTIVE', 'PENDING', 'REMOVED', name='teammembershipstatus', create_type=False), nullable=False, server_default='ACTIVE'),
            sa.Column('joined_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.Column('left_at', sa.TIMESTAMP(timezone=True), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
            sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('team_id', 'user_id', name='unique_team_user_membership')
        )
        op.create_index('idx_team_memberships_team_id', 'team_memberships', ['team_id'])
        op.create_index('idx_team_memberships_user_id', 'team_memberships', ['user_id'])
        op.create_index('idx_team_memberships_active', 'team_memberships', ['team_id', 'is_active'])

    # Create game player position enum
    if not enum_exists('gameplayerposition'):
        conn.execute(sa.text("CREATE TYPE gameplayerposition AS ENUM ('LEFT', 'RIGHT')"))

    # Create game player team side enum
    if not enum_exists('gameplayerteamside'):
        conn.execute(sa.text("CREATE TYPE gameplayerteamside AS ENUM ('TEAM_1', 'TEAM_2')"))

    # Add position tracking to game_players
    if not column_exists('game_players', 'position'):
        op.add_column('game_players', sa.Column('position', postgresql.ENUM('LEFT', 'RIGHT', name='gameplayerposition', create_type=False), nullable=True))
    
    if not column_exists('game_players', 'team_side'):
        op.add_column('game_players', sa.Column('team_side', postgresql.ENUM('TEAM_1', 'TEAM_2', name='gameplayerteamside', create_type=False), nullable=True))

    # Add foreign key constraints if they don't exist
    existing_fks = [fk['name'] for fk in inspector.get_foreign_keys('teams')]
    if 'fk_teams_created_by' not in existing_fks:
        op.create_foreign_key('fk_teams_created_by', 'teams', 'users', ['created_by'], ['id'])


def downgrade() -> None:
    """Downgrade schema - remove comprehensive game management enhancements."""
    
    # Get the connection and inspector
    conn = op.get_bind()
    inspector = inspect(conn)
    
    # Helper function to check if column exists
    def column_exists(table_name, column_name):
        try:
            columns = [col['name'] for col in inspector.get_columns(table_name)]
            return column_name in columns
        except Exception:
            return False
    
    # Helper function to check if table exists
    def table_exists(table_name):
        return inspector.has_table(table_name)
    
    # Remove position tracking from game_players
    if column_exists('game_players', 'team_side'):
        op.drop_column('game_players', 'team_side')
    
    if column_exists('game_players', 'position'):
        op.drop_column('game_players', 'position')

    # Drop team_memberships table
    if table_exists('team_memberships'):
        op.drop_table('team_memberships')

    # Remove team table extensions
    existing_fks = [fk['name'] for fk in inspector.get_foreign_keys('teams')]
    if 'fk_teams_created_by' in existing_fks:
        op.drop_constraint('fk_teams_created_by', 'teams', type_='foreignkey')
    
    if column_exists('teams', 'is_active'):
        op.drop_column('teams', 'is_active')
    
    if column_exists('teams', 'created_at'):
        op.drop_column('teams', 'created_at')
    
    if column_exists('teams', 'created_by'):
        op.drop_column('teams', 'created_by')
    
    if column_exists('teams', 'logo_url'):
        op.drop_column('teams', 'logo_url')
    
    if column_exists('teams', 'description'):
        op.drop_column('teams', 'description')

    # Remove privacy settings from users
    if column_exists('users', 'is_game_statistics_public'):
        op.drop_column('users', 'is_game_statistics_public')
    
    if column_exists('users', 'is_game_history_public'):
        op.drop_column('users', 'is_game_history_public')

    # Remove onboarding tracking from users
    if column_exists('users', 'onboarding_completed_at'):
        op.drop_column('users', 'onboarding_completed_at')
    
    if column_exists('users', 'onboarding_completed'):
        op.drop_column('users', 'onboarding_completed')

    # Drop enums - using raw SQL for PostgreSQL
    conn.execute(sa.text("DROP TYPE IF EXISTS gameplayerteamside"))
    conn.execute(sa.text("DROP TYPE IF EXISTS gameplayerposition"))
    conn.execute(sa.text("DROP TYPE IF EXISTS teammembershipstatus"))
    conn.execute(sa.text("DROP TYPE IF EXISTS teammembershiprole"))
