"""Consolidated migration for roles and court enums

Revision ID: 5e3a8f7b9d0c
Revises: c1a9add3b8f7
Create Date: 2025-06-10 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '5e3a8f7b9d0c'
down_revision: Union[str, None] = 'c1a9add3b8f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Enum definitions
surface_type_enum = postgresql.ENUM('Turf', 'Clay', 'Hard Court', 'Sand', name='surfacetype')
availability_status_enum = postgresql.ENUM('Available', 'Unavailable', 'Maintenance', name='courtavailabilitystatus')
user_role_new = postgresql.ENUM('player', 'admin', 'super-admin', name='userrole')


def upgrade() -> None:
    # ### Role Migration ###
    op.drop_column('users', 'is_admin')

    # Data is now handled in the previous migration, so these are not needed.
    # op.execute("UPDATE users SET role = 'admin' WHERE role = 'CLUB_ADMIN'")
    # op.execute("UPDATE users SET role = 'player' WHERE role = 'PLAYER'")

    # The userrole enum is created in the previous migration.
    # We just need to ensure the column type is correct.
    op.alter_column('users', 'role',
               type_=user_role_new,
               postgresql_using='role::userrole',
               existing_type=sa.VARCHAR(50)) # Assuming it might be varchar after manual fix
    
    op.create_index(op.f('ix_users_role'), 'users', ['role'], unique=False)
    
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

    # ### Court Enum Migration ###
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
    # Simplified downgrade for brevity
    op.drop_index(op.f('ix_users_role'), table_name='users')
    op.drop_index(op.f('ix_club_admins_id'), table_name='club_admins')
    op.drop_table('club_admins')
    op.add_column('users', sa.Column('is_admin', sa.BOOLEAN(), server_default=sa.text('false'), autoincrement=False, nullable=False))
    
    op.alter_column('users', 'role', type_=sa.VARCHAR(50))
    op.execute("DROP TYPE userrole")
    
    op.alter_column('courts', 'surface_type', type_=sa.VARCHAR())
    op.alter_column('courts', 'default_availability_status', type_=sa.VARCHAR())
    op.execute("DROP TYPE surfacetype")
    op.execute("DROP TYPE courtavailabilitystatus") 