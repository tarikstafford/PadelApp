"""Add tournament system tables

Revision ID: 20250627_111615_add_tournament_system
Revises: 5f1f2e2e1e0a
Create Date: 2025-06-27 11:16:15.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250627_111615_add_tournament_system'
down_revision = '5f1f2e2e1e0a'  # The initial migration
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create enum types using SQLAlchemy's ENUM type which handles creation automatically
    tournament_status_enum = postgresql.ENUM('DRAFT', 'REGISTRATION_OPEN', 'REGISTRATION_CLOSED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', name='tournamentstatus')
    tournament_type_enum = postgresql.ENUM('SINGLE_ELIMINATION', 'DOUBLE_ELIMINATION', 'AMERICANO', 'FIXED_AMERICANO', name='tournamenttype')
    tournament_category_enum = postgresql.ENUM('BRONZE', 'SILVER', 'GOLD', 'PLATINUM', name='tournamentcategory')
    match_status_enum = postgresql.ENUM('SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', 'WALKOVER', name='matchstatus')
    
    tournament_status_enum.create(op.get_bind())
    tournament_type_enum.create(op.get_bind())
    tournament_category_enum.create(op.get_bind())
    match_status_enum.create(op.get_bind())

    # Create tournaments table
    op.create_table('tournaments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('club_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('tournament_type', postgresql.ENUM('SINGLE_ELIMINATION', 'DOUBLE_ELIMINATION', 'AMERICANO', 'FIXED_AMERICANO', name='tournamenttype'), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=False),
        sa.Column('registration_deadline', sa.DateTime(), nullable=False),
        sa.Column('status', postgresql.ENUM('DRAFT', 'REGISTRATION_OPEN', 'REGISTRATION_CLOSED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', name='tournamentstatus'), nullable=False),
        sa.Column('max_participants', sa.Integer(), nullable=False),
        sa.Column('entry_fee', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['club_id'], ['clubs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tournaments_club_id'), 'tournaments', ['club_id'], unique=False)
    op.create_index(op.f('ix_tournaments_id'), 'tournaments', ['id'], unique=False)
    op.create_index(op.f('ix_tournaments_name'), 'tournaments', ['name'], unique=False)

    # Create tournament_category_configs table
    op.create_table('tournament_category_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tournament_id', sa.Integer(), nullable=False),
        sa.Column('category', postgresql.ENUM('BRONZE', 'SILVER', 'GOLD', 'PLATINUM', name='tournamentcategory'), nullable=False),
        sa.Column('max_participants', sa.Integer(), nullable=False),
        sa.Column('min_elo', sa.Float(), nullable=False),
        sa.Column('max_elo', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['tournament_id'], ['tournaments.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create tournament_teams table
    op.create_table('tournament_teams',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tournament_id', sa.Integer(), nullable=False),
        sa.Column('category_config_id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.Column('seed', sa.Integer(), nullable=True),
        sa.Column('average_elo', sa.Float(), nullable=False),
        sa.Column('registration_date', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['category_config_id'], ['tournament_category_configs.id'], ),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ),
        sa.ForeignKeyConstraint(['tournament_id'], ['tournaments.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create tournament_matches table
    op.create_table('tournament_matches',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tournament_id', sa.Integer(), nullable=False),
        sa.Column('category_config_id', sa.Integer(), nullable=False),
        sa.Column('team1_id', sa.Integer(), nullable=True),
        sa.Column('team2_id', sa.Integer(), nullable=True),
        sa.Column('round_number', sa.Integer(), nullable=False),
        sa.Column('match_number', sa.Integer(), nullable=False),
        sa.Column('scheduled_time', sa.DateTime(), nullable=True),
        sa.Column('court_id', sa.Integer(), nullable=True),
        sa.Column('status', postgresql.ENUM('SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', 'WALKOVER', name='matchstatus'), nullable=False),
        sa.Column('winning_team_id', sa.Integer(), nullable=True),
        sa.Column('team1_score', sa.Integer(), nullable=True),
        sa.Column('team2_score', sa.Integer(), nullable=True),
        sa.Column('game_id', sa.Integer(), nullable=True),
        sa.Column('winner_advances_to_match_id', sa.Integer(), nullable=True),
        sa.Column('loser_advances_to_match_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['category_config_id'], ['tournament_category_configs.id'], ),
        sa.ForeignKeyConstraint(['court_id'], ['courts.id'], ),
        sa.ForeignKeyConstraint(['game_id'], ['games.id'], ),
        sa.ForeignKeyConstraint(['loser_advances_to_match_id'], ['tournament_matches.id'], ),
        sa.ForeignKeyConstraint(['team1_id'], ['tournament_teams.id'], ),
        sa.ForeignKeyConstraint(['team2_id'], ['tournament_teams.id'], ),
        sa.ForeignKeyConstraint(['tournament_id'], ['tournaments.id'], ),
        sa.ForeignKeyConstraint(['winner_advances_to_match_id'], ['tournament_matches.id'], ),
        sa.ForeignKeyConstraint(['winning_team_id'], ['tournament_teams.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create tournament_court_bookings table
    op.create_table('tournament_court_bookings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tournament_id', sa.Integer(), nullable=False),
        sa.Column('court_id', sa.Integer(), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=False),
        sa.Column('is_occupied', sa.Boolean(), nullable=False),
        sa.Column('match_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['court_id'], ['courts.id'], ),
        sa.ForeignKeyConstraint(['match_id'], ['tournament_matches.id'], ),
        sa.ForeignKeyConstraint(['tournament_id'], ['tournaments.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create tournament_trophies table
    op.create_table('tournament_trophies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tournament_id', sa.Integer(), nullable=False),
        sa.Column('category_config_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('trophy_type', sa.String(), nullable=False),
        sa.Column('awarded_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['category_config_id'], ['tournament_category_configs.id'], ),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ),
        sa.ForeignKeyConstraint(['tournament_id'], ['tournaments.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('tournament_trophies')
    op.drop_table('tournament_court_bookings')
    op.drop_table('tournament_matches')
    op.drop_table('tournament_teams')
    op.drop_table('tournament_category_configs')
    op.drop_index(op.f('ix_tournaments_name'), table_name='tournaments')
    op.drop_index(op.f('ix_tournaments_id'), table_name='tournaments')
    op.drop_index(op.f('ix_tournaments_club_id'), table_name='tournaments')
    op.drop_table('tournaments')
    
    # Drop enum types using SQLAlchemy
    match_status_enum = postgresql.ENUM(name='matchstatus')
    tournament_category_enum = postgresql.ENUM(name='tournamentcategory')
    tournament_type_enum = postgresql.ENUM(name='tournamenttype')
    tournament_status_enum = postgresql.ENUM(name='tournamentstatus')
    
    match_status_enum.drop(op.get_bind())
    tournament_category_enum.drop(op.get_bind())
    tournament_type_enum.drop(op.get_bind())
    tournament_status_enum.drop(op.get_bind())