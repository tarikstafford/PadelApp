"""Initial migration with all models

Revision ID: e1f59e29f633
Revises: 
Create Date: 2025-06-06 04:10:49.278385

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'e1f59e29f633'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enum types
    bookingstatus_enum = postgresql.ENUM('PENDING', 'CONFIRMED', 'CANCELLED', 'COMPLETED', name='bookingstatus')
    gametype_enum = postgresql.ENUM('PUBLIC', 'PRIVATE', name='gametype')
    gameplayerstatus_enum = postgresql.ENUM('INVITED', 'ACCEPTED', 'DECLINED', 'REQUESTED_TO_JOIN', name='gameplayerstatus')
    user_role_enum = postgresql.ENUM('player', 'admin', 'super-admin', name='userrole')
    surface_type_enum = postgresql.ENUM('Turf', 'Clay', 'Hard Court', 'Sand', name='surfacetype')
    availability_status_enum = postgresql.ENUM('Available', 'Unavailable', 'Maintenance', name='courtavailabilitystatus')

    bookingstatus_enum.create(op.get_bind(), checkfirst=True)
    gametype_enum.create(op.get_bind(), checkfirst=True)
    gameplayerstatus_enum.create(op.get_bind(), checkfirst=True)
    user_role_enum.create(op.get_bind(), checkfirst=True)
    surface_type_enum.create(op.get_bind(), checkfirst=True)
    availability_status_enum.create(op.get_bind(), checkfirst=True)

    # Tables
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('profile_picture_url', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('role', user_role_enum, nullable=False, server_default='player'),
        sa.PrimaryKeyConstraint('id'),
        if_not_exists=True
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True, if_not_exists=True)
    
    op.create_table('clubs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=True),
        sa.Column('address', sa.String(), nullable=True),
        sa.Column('city', sa.String(), nullable=True),
        sa.Column('postal_code', sa.String(), nullable=True),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('opening_hours', sa.Text(), nullable=True),
        sa.Column('amenities', sa.Text(), nullable=True),
        sa.Column('image_url', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        if_not_exists=True
    )
    op.create_index(op.f('ix_clubs_city'), 'clubs', ['city'], unique=False, if_not_exists=True)
    op.create_index(op.f('ix_clubs_email'), 'clubs', ['email'], unique=False, if_not_exists=True)
    op.create_index(op.f('ix_clubs_id'), 'clubs', ['id'], unique=False, if_not_exists=True)
    op.create_index(op.f('ix_clubs_name'), 'clubs', ['name'], unique=False, if_not_exists=True)
    op.create_index(op.f('ix_clubs_postal_code'), 'clubs', ['postal_code'], unique=False, if_not_exists=True)

    op.create_table('club_admins',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('club_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['club_id'], ['clubs.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'club_id', name='_user_club_uc'),
        if_not_exists=True
    )
    
    op.create_table('courts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('club_id', sa.Integer(), nullable=False),
        sa.Column('surface_type', surface_type_enum, nullable=True),
        sa.Column('is_indoor', sa.Boolean(), nullable=True),
        sa.Column('price_per_hour', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('default_availability_status', availability_status_enum, nullable=True),
        sa.ForeignKeyConstraint(['club_id'], ['clubs.id'], ),
        sa.PrimaryKeyConstraint('id'),
        if_not_exists=True
    )
    op.create_index(op.f('ix_courts_id'), 'courts', ['id'], unique=False, if_not_exists=True)
    op.create_index(op.f('ix_courts_name'), 'courts', ['name'], unique=False, if_not_exists=True)

    op.create_table('bookings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('court_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('start_time', sa.DateTime(), nullable=False),
    sa.Column('end_time', sa.DateTime(), nullable=False),
    sa.Column('status', bookingstatus_enum, nullable=False),
    sa.ForeignKeyConstraint(['court_id'], ['courts.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    if_not_exists=True
    )
    op.create_index(op.f('ix_bookings_id'), 'bookings', ['id'], unique=False, if_not_exists=True)

    op.create_table('games',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('booking_id', sa.Integer(), nullable=False),
    sa.Column('game_type', gametype_enum, nullable=False),
    sa.Column('skill_level', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['booking_id'], ['bookings.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('booking_id'),
    if_not_exists=True
    )
    op.create_index(op.f('ix_games_id'), 'games', ['id'], unique=False, if_not_exists=True)

    op.create_table('game_players',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('game_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('status', gameplayerstatus_enum, nullable=False),
    sa.ForeignKeyConstraint(['game_id'], ['games.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    if_not_exists=True
    )
    op.create_index(op.f('ix_game_players_id'), 'game_players', ['id'], unique=False, if_not_exists=True)


def downgrade() -> None:
    # Simplified for brevity
    op.drop_index(op.f('ix_game_players_id'), table_name='game_players')
    op.drop_table('game_players')
    op.drop_index(op.f('ix_games_id'), table_name='games')
    op.drop_table('games')
    op.drop_index(op.f('ix_bookings_id'), table_name='bookings')
    op.drop_table('bookings')
    op.drop_index(op.f('ix_courts_name'), table_name='courts')
    op.drop_index(op.f('ix_courts_id'), table_name='courts')
    op.drop_table('courts')
    op.drop_table('club_admins')
    op.drop_index(op.f('ix_clubs_postal_code'), table_name='clubs')
    op.drop_index(op.f('ix_clubs_name'), table_name='clubs')
    op.drop_index(op.f('ix_clubs_id'), table_name='clubs')
    op.drop_index(op.f('ix_clubs_email'), table_name='clubs')
    op.drop_index(op.f('ix_clubs_city'), table_name='clubs')
    op.drop_table('clubs')
    op.drop_table('users')
    op.execute('DROP TYPE bookingstatus;')
    op.execute('DROP TYPE gametype;')
    op.execute('DROP TYPE gameplayerstatus;')
    op.execute('DROP TYPE userrole;')
    op.execute('DROP TYPE surfacetype;')
    op.execute('DROP TYPE courtavailabilitystatus;') 