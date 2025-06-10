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

    # --- Start of Definitive Enum Migration ---

    # 1. Alter column to VARCHAR to allow for arbitrary string values temporarily
    op.alter_column('users', 'role',
               type_=sa.VARCHAR(50),
               postgresql_using='role::text::varchar')

    # 2. Update the data to the new values
    op.execute("UPDATE users SET role = 'admin' WHERE role = 'CLUB_ADMIN'")
    op.execute("UPDATE users SET role = 'player' WHERE role = 'PLAYER'")
    
    # 3. Clean up all old enum types safely
    op.execute("DROP TYPE IF EXISTS userrole_old")
    op.execute("DROP TYPE IF EXISTS userrole")
    
    # 4. Create the new enum type
    user_role_new = postgresql.ENUM('player', 'admin', 'super-admin', name='userrole')
    user_role_new.create(op.get_bind())

    # 5. Alter the column back to the new ENUM type
    op.alter_column('users', 'role',
               type_=user_role_new,
               postgresql_using='role::userrole')

    # --- End of Definitive Enum Migration ---

    # Add index to role column
    op.create_index(op.f('ix_users_role'), 'users', ['role'], unique=False)


def downgrade() -> None:
    # Simplified downgrade. A full production downgrade would need to be more careful.
    op.drop_index(op.f('ix_users_role'), table_name='users')
    op.drop_index(op.f('ix_club_admins_id'), table_name='club_admins')
    op.drop_table('club_admins')
    op.execute("DROP TYPE IF EXISTS userrole")
    op.add_column('users', sa.Column('is_admin', sa.BOOLEAN(), server_default=sa.text('false'), autoincrement=False, nullable=False))
    # Note: Downgrading the role column and its data is complex and omitted here. 