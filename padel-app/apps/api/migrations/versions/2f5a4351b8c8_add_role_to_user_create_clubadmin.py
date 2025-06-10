"""Add role to User, create ClubAdmin, and add indexes

Revision ID: 2f5a4351b8c8
Revises: c1a9add3b8f7
Create Date: 2025-06-08 05:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2f5a4351b8c8'
down_revision: Union[str, None] = 'c1a9add3b8f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop is_admin column from users table
    op.drop_column('users', 'is_admin')

    # Create club_admins table
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

    # Update UserRole enum
    # First, let's rename the old enum to avoid conflicts
    op.execute("ALTER TYPE userrole RENAME TO userrole_old")
    
    # Create the new enum
    user_role_new = postgresql.ENUM('player', 'admin', 'super-admin', name='userrole')
    user_role_new.create(op.get_bind())

    # Update existing data to match new enum values before altering the column
    op.execute("UPDATE users SET role = 'admin' WHERE role = 'CLUB_ADMIN'")
    op.execute("UPDATE users SET role = 'player' WHERE role = 'PLAYER'")

    # Update the column to use the new enum
    # We need to do this using a temporary column because we can't cast directly
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE userrole USING role::text::userrole")
    
    # Drop the old enum
    op.execute("DROP TYPE userrole_old")

    # Add index to role column
    op.create_index(op.f('ix_users_role'), 'users', ['role'], unique=False)


def downgrade() -> None:
    # Drop index from role column
    op.drop_index(op.f('ix_users_role'), table_name='users')

    # Revert UserRole enum
    op.execute("ALTER TYPE userrole RENAME TO userrole_new")
    user_role_old = postgresql.ENUM('PLAYER', 'CLUB_ADMIN', name='userrole')
    user_role_old.create(op.get_bind())
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE userrole USING role::text::userrole")
    op.execute("DROP TYPE userrole_new")

    # Drop club_admins table
    op.drop_index(op.f('ix_club_admins_id'), table_name='club_admins')
    op.drop_table('club_admins')

    # Add back is_admin column
    op.add_column('users', sa.Column('is_admin', sa.BOOLEAN(), server_default=sa.text('false'), autoincrement=False, nullable=False)) 