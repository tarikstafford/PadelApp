"""Manually add booking_id to games table

Revision ID: c065e20230f5
Revises: a91bbeaea52f
Create Date: 2025-06-11 09:33:04.996160

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c065e20230f5'
down_revision = 'a91bbeaea52f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('games', sa.Column('booking_id', sa.Integer(), nullable=False))
    op.create_foreign_key(
        'fk_games_booking_id',
        'games', 'bookings',
        ['booking_id'], ['id']
    )
    op.create_unique_constraint('uq_games_booking_id', 'games', ['booking_id'])


def downgrade() -> None:
    op.drop_constraint('uq_games_booking_id', 'games', type_='unique')
    op.drop_constraint('fk_games_booking_id', 'games', type_='foreignkey')
    op.drop_column('games', 'booking_id') 