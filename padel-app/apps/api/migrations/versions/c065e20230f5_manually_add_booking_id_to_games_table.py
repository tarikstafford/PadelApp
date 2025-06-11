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
    pass


def downgrade() -> None:
    pass 