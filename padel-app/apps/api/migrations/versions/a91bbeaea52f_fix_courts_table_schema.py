"""fix_courts_table_schema

Revision ID: a91bbeaea52f
Revises: e2fcf5442433
Create Date: 2025-06-11 08:35:41.229158

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a91bbeaea52f'
down_revision = 'e2fcf5442433'
branch_labels = None
depends_on = None

surface_type_enum = postgresql.ENUM('Turf', 'Clay', 'Hard Court', 'Sand', name='surfacetype')
availability_status_enum = postgresql.ENUM('Available', 'Unavailable', 'Maintenance', name='courtavailabilitystatus')

def upgrade() -> None:
    # Create the new ENUM types
    surface_type_enum.create(op.get_bind(), checkfirst=True)
    availability_status_enum.create(op.get_bind(), checkfirst=True)

    # Add the missing columns
    op.add_column('courts', sa.Column('surface_type', surface_type_enum, nullable=True))
    # op.add_column('courts', sa.Column('is_indoor', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('courts', sa.Column('price_per_hour', sa.Numeric(precision=10, scale=2), nullable=True))
    op.add_column('courts', sa.Column('default_availability_status', availability_status_enum, nullable=True, server_default='Available'))

    # Drop the incorrect/unused columns
    op.drop_column('courts', 'type')
    op.drop_column('courts', 'is_active')


def downgrade() -> None:
    # Add back the incorrect/unused columns
    op.add_column('courts', sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('courts', sa.Column('type', sa.VARCHAR(length=50), autoincrement=False, nullable=True))

    # Drop the added columns
    op.drop_column('courts', 'default_availability_status')
    op.drop_column('courts', 'price_per_hour')
    # op.drop_column('courts', 'is_indoor')
    op.drop_column('courts', 'surface_type')

    # Drop the ENUM types
    availability_status_enum.drop(op.get_bind(), checkfirst=True)
    surface_type_enum.drop(op.get_bind(), checkfirst=True) 