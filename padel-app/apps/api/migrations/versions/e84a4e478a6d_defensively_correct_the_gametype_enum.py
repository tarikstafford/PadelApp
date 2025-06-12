"""Defensively correct the gametype enum

Revision ID: e84a4e478a6d
Revises: '145e9c6a294a'
Create Date: 2025-06-12 14:13:21.722985

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e84a4e478a6d'
down_revision = '145e9c6a294a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Alter column to VARCHAR to remove ENUM constraint
    op.alter_column('games', 'game_type',
        existing_type=sa.Enum('public', 'private', name='gametype'),
        type_=sa.String(length=50),
        existing_nullable=False)

    # 2. Update existing data to uppercase
    op.execute("UPDATE games SET game_type = UPPER(game_type)")

    # 3. Drop the old enum type
    op.execute("DROP TYPE IF EXISTS gametype CASCADE")

    # 4. Create the new enum type with uppercase values
    op.execute("CREATE TYPE gametype AS ENUM('PUBLIC', 'PRIVATE')")

    # 5. Alter column back to the new ENUM type
    op.alter_column('games', 'game_type',
        existing_type=sa.String(length=50),
        type_=sa.Enum('PUBLIC', 'PRIVATE', name='gametype', create_type=False),
        existing_nullable=False,
        postgresql_using='game_type::gametype')


def downgrade() -> None:
    # This is a corrective migration; a full downgrade is complex. 
    # For simplicity, we'll just handle the column and type.
    op.alter_column('games', 'game_type',
        existing_type=sa.Enum('PUBLIC', 'PRIVATE', name='gametype'),
        type_=sa.String(length=50),
        existing_nullable=False)
        
    op.execute("UPDATE games SET game_type = LOWER(game_type)")
    
    op.execute("DROP TYPE IF EXISTS gametype CASCADE")
    
    op.execute("CREATE TYPE gametype AS ENUM('public', 'private')")
    
    op.alter_column('games', 'game_type',
        existing_type=sa.String(length=50),
        type_=sa.Enum('public', 'private', name='gametype', create_type=False),
        existing_nullable=False,
        postgresql_using='game_type::gametype') 