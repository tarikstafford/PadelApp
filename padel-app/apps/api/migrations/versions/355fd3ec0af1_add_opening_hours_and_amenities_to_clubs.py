"""add_opening_hours_and_amenities_to_clubs

Revision ID: 355fd3ec0af1
Revises: 9fb8c0665eb1
Create Date: 2025-06-11 07:29:43.149234

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '355fd3ec0af1'
down_revision = '9fb8c0665eb1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('clubs', sa.Column('opening_hours', sa.String(), nullable=True))
    op.add_column('clubs', sa.Column('amenities', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('clubs', 'amenities')
    op.drop_column('clubs', 'opening_hours') 