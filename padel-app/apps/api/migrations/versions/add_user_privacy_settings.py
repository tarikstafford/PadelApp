"""add user privacy settings

Revision ID: add_user_privacy_settings
Revises: e8e8874a165c
Create Date: 2024-07-10 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_user_privacy_settings'
down_revision = 'e8e8874a165c'
branch_labels = None
depends_on = None


def upgrade():
    # Add privacy settings columns to users table
    op.add_column('users', sa.Column('is_game_history_public', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('users', sa.Column('is_game_statistics_public', sa.Boolean(), nullable=False, server_default='true'))


def downgrade():
    # Remove privacy settings columns from users table
    op.drop_column('users', 'is_game_statistics_public')
    op.drop_column('users', 'is_game_history_public')