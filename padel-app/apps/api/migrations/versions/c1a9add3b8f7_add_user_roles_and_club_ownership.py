"""Add user roles and club ownership

Revision ID: c1a9add3b8f7
Revises: e1f59e29f633
Create Date: 2025-06-08 04:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import table, column

# revision identifiers, used by Alembic.
revision: str = 'c1a9add3b8f7'
down_revision: Union[str, None] = 'e1f59e29f633'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Enum definitions
surface_type_enum = postgresql.ENUM('Turf', 'Clay', 'Hard Court', 'Sand', name='surfacetype')
availability_status_enum = postgresql.ENUM('Available', 'Unavailable', 'Maintenance', name='courtavailabilitystatus')
user_role_enum = postgresql.ENUM('player', 'admin', 'super-admin', name='userrole')

def upgrade() -> None:
    # ### User Role and Ownership ###
    user_role_enum.create(op.get_bind(), checkfirst=True)
    op.add_column('users', sa.Column('role', user_role_enum, nullable=True))
    op.execute("UPDATE users SET role = 'player' WHERE role IS NULL")
    op.alter_column('users', 'role', nullable=False)
    
    op.add_column('clubs', sa.Column('owner_id', sa.Integer(), nullable=True))
    
    op.create_foreign_key('fk_clubs_owner_id_users', 'clubs', 'users', ['owner_id'], ['id'])
    
    # ### ClubAdmin Table ###
    op.create_table('club_admins',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('club_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['club_id'], ['clubs.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'club_id', name='_user_club_uc')
    )
    op.create_index(op.f('ix_club_admins_id'), 'club_admins', ['id'], unique=False)
    
    # ### Court Enums ###
    surface_type_enum.create(op.get_bind(), checkfirst=True)
    availability_status_enum.create(op.get_bind(), checkfirst=True)
    
    op.alter_column('courts', 'surface_type',
               type_=surface_type_enum,
               postgresql_using='surface_type::surfacetype',
               existing_type=sa.VARCHAR(),
               nullable=True)

    op.alter_column('courts', 'default_availability_status',
               type_=availability_status_enum,
               postgresql_using='default_availability_status::courtavailabilitystatus',
               existing_type=sa.VARCHAR(),
               nullable=True)


def downgrade() -> None:
    # Simplified downgrade
    op.drop_constraint('fk_clubs_owner_id_users', 'clubs', type_='foreignkey')
    op.drop_column('clubs', 'owner_id')
    op.drop_column('users', 'role')
    user_role_enum.drop(op.get_bind())
    
    op.drop_index(op.f('ix_club_admins_id'), table_name='club_admins')
    op.drop_table('club_admins')
    
    op.alter_column('courts', 'surface_type', type_=sa.VARCHAR())
    op.alter_column('courts', 'default_availability_status', type_=sa.VARCHAR())
    surface_type_enum.drop(op.get_bind())
    availability_status_enum.drop(op.get_bind()) 