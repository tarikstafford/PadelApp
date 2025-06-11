"""rename_zip_code_to_postal_code_on_clubs_table

Revision ID: 34a3bee92f6f
Revises: 5d692e4c52a1
Create Date: 2025-06-11 05:22:18.157503

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '34a3bee92f6f'
down_revision = '5d692e4c52a1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('clubs', 'zip_code', new_column_name='postal_code', existing_type=sa.String(length=20))


def downgrade() -> None:
    op.alter_column('clubs', 'postal_code', new_column_name='zip_code', existing_type=sa.String(length=20)) 