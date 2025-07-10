"""comprehensive_game_management_enhancements

Revision ID: d5c986b34c46
Revises: 5983356438f4
Create Date: 2025-07-10 14:46:01.339357

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd5c986b34c46'
down_revision: Union[str, None] = '5983356438f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema with comprehensive game management enhancements."""
    
    # Add onboarding tracking to users table
    try:
        op.add_column('users', sa.Column('onboarding_completed', sa.Boolean(), nullable=False, server_default='false'))
    except Exception:
        pass  # Column already exists
    
    try:
        op.add_column('users', sa.Column('onboarding_completed_at', sa.TIMESTAMP(timezone=True), nullable=True))
    except Exception:
        pass  # Column already exists

    # Add privacy settings to users table
    try:
        op.add_column('users', sa.Column('is_game_history_public', sa.Boolean(), nullable=False, server_default='true'))
    except Exception:
        pass  # Column already exists
    
    try:
        op.add_column('users', sa.Column('is_game_statistics_public', sa.Boolean(), nullable=False, server_default='true'))
    except Exception:
        pass  # Column already exists

    # Extend teams table for persistence
    try:
        op.add_column('teams', sa.Column('description', sa.Text(), nullable=True))
    except Exception:
        pass  # Column already exists
    
    try:
        op.add_column('teams', sa.Column('logo_url', sa.String(), nullable=True))
    except Exception:
        pass  # Column already exists
    
    try:
        op.add_column('teams', sa.Column('created_by', sa.Integer(), nullable=True))
    except Exception:
        pass  # Column already exists
    
    try:
        op.add_column('teams', sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')))
    except Exception:
        pass  # Column already exists
    
    try:
        op.add_column('teams', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))
    except Exception:
        pass  # Column already exists

    # Create team membership role enum
    try:
        team_role_enum = sa.Enum('OWNER', 'ADMIN', 'MEMBER', name='teammembershiprole')
        team_role_enum.create(op.get_bind(), checkfirst=True)
    except Exception:
        pass  # Enum already exists

    # Create team membership status enum
    try:
        team_status_enum = sa.Enum('ACTIVE', 'INACTIVE', 'PENDING', 'REMOVED', name='teammembershipstatus')
        team_status_enum.create(op.get_bind(), checkfirst=True)
    except Exception:
        pass  # Enum already exists

    # Create team_memberships table
    try:
        op.create_table('team_memberships',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('team_id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('role', sa.Enum('OWNER', 'ADMIN', 'MEMBER', name='teammembershiprole'), nullable=False, server_default='MEMBER'),
            sa.Column('status', sa.Enum('ACTIVE', 'INACTIVE', 'PENDING', 'REMOVED', name='teammembershipstatus'), nullable=False, server_default='ACTIVE'),
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
    except Exception:
        pass  # Table already exists

    # Create game player position enum
    try:
        position_enum = sa.Enum('LEFT', 'RIGHT', name='gameplayerposition')
        position_enum.create(op.get_bind(), checkfirst=True)
    except Exception:
        pass  # Enum already exists

    # Create game player team side enum
    try:
        team_side_enum = sa.Enum('TEAM_1', 'TEAM_2', name='gameplayerteamside')
        team_side_enum.create(op.get_bind(), checkfirst=True)
    except Exception:
        pass  # Enum already exists

    # Add position tracking to game_players
    try:
        op.add_column('game_players', sa.Column('position', sa.Enum('LEFT', 'RIGHT', name='gameplayerposition'), nullable=True))
    except Exception:
        pass  # Column already exists
    
    try:
        op.add_column('game_players', sa.Column('team_side', sa.Enum('TEAM_1', 'TEAM_2', name='gameplayerteamside'), nullable=True))
    except Exception:
        pass  # Column already exists

    # Add foreign key constraints if they don't exist
    try:
        op.create_foreign_key('fk_teams_created_by', 'teams', 'users', ['created_by'], ['id'])
    except Exception:
        pass  # Constraint already exists


def downgrade() -> None:
    """Downgrade schema - remove comprehensive game management enhancements."""
    
    # Remove position tracking from game_players
    try:
        op.drop_column('game_players', 'team_side')
    except Exception:
        pass
    
    try:
        op.drop_column('game_players', 'position')
    except Exception:
        pass

    # Drop team_memberships table
    try:
        op.drop_table('team_memberships')
    except Exception:
        pass

    # Remove team table extensions
    try:
        op.drop_constraint('fk_teams_created_by', 'teams', type_='foreignkey')
    except Exception:
        pass
    
    try:
        op.drop_column('teams', 'is_active')
    except Exception:
        pass
    
    try:
        op.drop_column('teams', 'created_at')
    except Exception:
        pass
    
    try:
        op.drop_column('teams', 'created_by')
    except Exception:
        pass
    
    try:
        op.drop_column('teams', 'logo_url')
    except Exception:
        pass
    
    try:
        op.drop_column('teams', 'description')
    except Exception:
        pass

    # Remove privacy settings from users
    try:
        op.drop_column('users', 'is_game_statistics_public')
    except Exception:
        pass
    
    try:
        op.drop_column('users', 'is_game_history_public')
    except Exception:
        pass

    # Remove onboarding tracking from users
    try:
        op.drop_column('users', 'onboarding_completed_at')
    except Exception:
        pass
    
    try:
        op.drop_column('users', 'onboarding_completed')
    except Exception:
        pass

    # Drop enums
    try:
        sa.Enum(name='gameplayerteamside').drop(op.get_bind(), checkfirst=True)
    except Exception:
        pass
    
    try:
        sa.Enum(name='gameplayerposition').drop(op.get_bind(), checkfirst=True)
    except Exception:
        pass
    
    try:
        sa.Enum(name='teammembershipstatus').drop(op.get_bind(), checkfirst=True)
    except Exception:
        pass
    
    try:
        sa.Enum(name='teammembershiprole').drop(op.get_bind(), checkfirst=True)
    except Exception:
        pass
