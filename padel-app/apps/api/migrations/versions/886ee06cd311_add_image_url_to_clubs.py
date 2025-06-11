"""add_image_url_to_clubs

Revision ID: 886ee06cd311
Revises: 355fd3ec0af1
Create Date: 2025-06-11 07:44:09.110214

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '886ee06cd311'
down_revision = '355fd3ec0af1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('clubs', sa.Column('image_url', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('clubs', 'image_url') 