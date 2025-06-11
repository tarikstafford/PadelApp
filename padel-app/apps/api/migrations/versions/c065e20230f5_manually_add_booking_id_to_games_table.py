"""Manually add booking_id to games table

Revision ID: c065e20230f5
Revises: a91bbeaea52f
Create Date: 2025-06-11 09:33:04.996160

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'c065e20230f5'
down_revision = 'a91bbeaea52f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create the ENUM type for game_type
    game_type_enum = postgresql.ENUM('public', 'private', name='gametype')
    game_type_enum.create(op.get_bind(), checkfirst=True)

    # Add columns to games table
    op.add_column('games', sa.Column('booking_id', sa.Integer(), nullable=False))
    op.add_column('games', sa.Column('game_type', game_type_enum, nullable=False, server_default='private'))
    op.add_column('games', sa.Column('skill_level', sa.String(), nullable=True))
    
    op.create_foreign_key(
        'fk_games_booking_id',
        'games', 'bookings',
        ['booking_id'], ['id']
    )
    op.create_unique_constraint('uq_games_booking_id', 'games', ['booking_id'])


def downgrade() -> None:
    op.drop_constraint('uq_games_booking_id', 'games', type_='unique')
    op.drop_constraint('fk_games_booking_id', 'games', type_='foreignkey')
    op.drop_column('games', 'skill_level')
    op.drop_column('games', 'game_type')
    op.drop_column('games', 'booking_id')
    
    # Drop the ENUM type
    game_type_enum = postgresql.ENUM('public', 'private', name='gametype')
    game_type_enum.drop(op.get_bind(), checkfirst=True) 