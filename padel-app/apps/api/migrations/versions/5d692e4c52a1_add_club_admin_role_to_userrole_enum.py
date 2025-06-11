"""add_club_admin_role_to_userrole_enum

Revision ID: 5d692e4c52a1
Revises: 9e957c939259
Create Date: 2025-06-11 05:13:31.954507

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5d692e4c52a1'
down_revision = '9e957c939259'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'club_admin'")


def downgrade() -> None:
    # Downgrading enums is often complex; for this case, we'll do nothing.
    # If this value were ever used, removing it would cause data integrity issues.
    pass 