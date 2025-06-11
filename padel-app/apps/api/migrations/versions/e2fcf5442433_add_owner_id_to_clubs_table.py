"""add_owner_id_to_clubs_table

Revision ID: e2fcf5442433
Revises: 886ee06cd311
Create Date: 2025-06-11 07:56:06.849182

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e2fcf5442433'
down_revision = '886ee06cd311'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('clubs', sa.Column('owner_id', sa.Integer(), nullable=False))
    op.create_foreign_key(
        'fk_clubs_owner_id_users',
        'clubs', 'users',
        ['owner_id'], ['id']
    )


def downgrade() -> None:
    op.drop_constraint('fk_clubs_owner_id_users', 'clubs', type_='foreignkey')
    op.drop_column('clubs', 'owner_id') 