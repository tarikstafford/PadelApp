"""Update court surface and status to enums

Revision ID: 860b6482a629
Revises: c1a9add3b8f7
Create Date: 2025-06-08 04:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from typing import Union, Sequence
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '860b6482a629'
down_revision: Union[str, None] = 'c1a9add3b8f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Correct, final ENUM definitions
surface_type_enum = postgresql.ENUM('Turf', 'Clay', 'Hard Court', 'Sand', name='surfacetype')
availability_status_enum = postgresql.ENUM('Available', 'Unavailable', 'Maintenance', name='courtavailabilitystatus')

def upgrade() -> None:
    # Create the new ENUM types with the correct values
    surface_type_enum.create(op.get_bind(), checkfirst=True)
    availability_status_enum.create(op.get_bind(), checkfirst=True)

    # Clean up old, messy data by mapping it to the new, correct values
    op.execute("UPDATE courts SET surface_type = 'Turf' WHERE surface_type IN ('Artificial Grass', 'Artificial Grass Pro', 'Sand-filled Synthetic')")
    op.execute("UPDATE courts SET surface_type = 'Hard Court' WHERE surface_type IN ('Hard', 'Cushioned Hard Court', 'ConcreteTextured', 'Panoramic Glass')")
    op.execute("UPDATE courts SET surface_type = 'Clay' WHERE surface_type = 'Clay'")
    op.execute("UPDATE courts SET surface_type = 'Sand' WHERE surface_type = 'Sand'")
    
    # Now that the data is clean, we can alter the column type
    op.alter_column('courts', 'surface_type',
               type_=surface_type_enum,
               postgresql_using='surface_type::surfacetype')

    op.alter_column('courts', 'default_availability_status',
               type_=availability_status_enum,
               postgresql_using='default_availability_status::courtavailabilitystatus')

def downgrade() -> None:
    # Revert the column types back to VARCHAR
    op.alter_column('courts', 'surface_type',
               type_=sa.VARCHAR(),
               postgresql_using='surface_type::varchar')
    op.alter_column('courts', 'default_availability_status',
               type_=sa.VARCHAR(),
               postgresql_using='default_availability_status::varchar')

    # Drop the ENUM types
    surface_type_enum.drop(op.get_bind())
    availability_status_enum.drop(op.get_bind()) 