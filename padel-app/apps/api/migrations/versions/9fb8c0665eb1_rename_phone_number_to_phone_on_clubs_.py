"""rename_phone_number_to_phone_on_clubs_table

Revision ID: 9fb8c0665eb1
Revises: 34a3bee92f6f
Create Date: 2025-06-11 06:17:41.970222

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9fb8c0665eb1'
down_revision = '34a3bee92f6f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('clubs', 'phone_number', new_column_name='phone', existing_type=sa.String(length=20))


def downgrade() -> None:
    op.alter_column('clubs', 'phone', new_column_name='phone_number', existing_type=sa.String(length=20)) 