"""Add tournament enhancements: recurring tournaments, participant tracking, hourly scheduling

Revision ID: add_tournament_enhancements
Revises: 627120000tsafe
Create Date: 2025-01-07 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_tournament_enhancements'
down_revision = '627120000tsafe'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create recurrence pattern enum
    recurrence_pattern_enum = postgresql.ENUM(
        'WEEKLY', 'MONTHLY', 'CUSTOM',
        name='recurrencepattern',
        create_type=False
    )
    recurrence_pattern_enum.create(op.get_bind(), checkfirst=True)

    # Create recurring_tournaments table
    op.create_table('recurring_tournaments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('club_id', sa.Integer(), nullable=False),
        sa.Column('series_name', sa.String(), nullable=False),
        sa.Column('recurrence_pattern', recurrence_pattern_enum, nullable=False),
        sa.Column('days_of_week', postgresql.ARRAY(sa.Integer()), nullable=True),
        sa.Column('day_of_month', sa.Integer(), nullable=True),
        sa.Column('interval_value', sa.Integer(), nullable=False),
        sa.Column('series_start_date', sa.Date(), nullable=False),
        sa.Column('series_end_date', sa.Date(), nullable=True),
        sa.Column('tournament_type', postgresql.ENUM('SINGLE_ELIMINATION', 'DOUBLE_ELIMINATION', 'AMERICANO', 'FIXED_AMERICANO', name='tournamenttype'), nullable=False),
        sa.Column('template_name', sa.String(), nullable=False),
        sa.Column('template_description', sa.Text(), nullable=True),
        sa.Column('entry_fee', sa.Float(), nullable=True),
        sa.Column('auto_generation_enabled', sa.Boolean(), nullable=False),
        sa.Column('generate_days_ahead', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False),
        sa.ForeignKeyConstraint(['club_id'], ['clubs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_recurring_tournaments_club_id'), 'recurring_tournaments', ['club_id'], unique=False)
    op.create_index(op.f('ix_recurring_tournaments_id'), 'recurring_tournaments', ['id'], unique=False)

    # Create recurring_tournament_category_templates table
    op.create_table('recurring_tournament_category_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('recurring_tournament_id', sa.Integer(), nullable=False),
        sa.Column('category', postgresql.ENUM('BRONZE', 'SILVER', 'GOLD', 'PLATINUM', name='tournamentcategory'), nullable=False),
        sa.Column('max_participants', sa.Integer(), nullable=False),
        sa.Column('min_elo', sa.Float(), nullable=False),
        sa.Column('max_elo', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['recurring_tournament_id'], ['recurring_tournaments.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_recurring_tournament_category_templates_recurring_tournament_id'), 'recurring_tournament_category_templates', ['recurring_tournament_id'], unique=False)

    # Create tournament_participants table
    op.create_table('tournament_participants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tournament_id', sa.Integer(), nullable=False),
        sa.Column('category_config_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('elo_at_registration', sa.Float(), nullable=False),
        sa.Column('seed_position', sa.Integer(), nullable=True),
        sa.Column('match_teams', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('registration_date', sa.TIMESTAMP(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['category_config_id'], ['tournament_category_configs.id'], ),
        sa.ForeignKeyConstraint(['tournament_id'], ['tournaments.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tournament_id', 'user_id', name='unique_participant_per_tournament')
    )
    op.create_index(op.f('ix_tournament_participants_tournament_id'), 'tournament_participants', ['tournament_id'], unique=False)
    op.create_index(op.f('ix_tournament_participants_user_id'), 'tournament_participants', ['user_id'], unique=False)

    # Add new columns to tournaments table
    op.add_column('tournaments', sa.Column('recurring_tournament_id', sa.Integer(), nullable=True))
    op.add_column('tournaments', sa.Column('auto_schedule_enabled', sa.Boolean(), nullable=True))
    op.add_column('tournaments', sa.Column('hourly_time_slots', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('tournaments', sa.Column('assigned_court_ids', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('tournaments', sa.Column('schedule_generated', sa.Boolean(), nullable=True))
    
    # Add foreign key constraint
    op.create_foreign_key(None, 'tournaments', 'recurring_tournaments', ['recurring_tournament_id'], ['id'])


def downgrade() -> None:
    # Remove foreign key constraint
    op.drop_constraint(None, 'tournaments', type_='foreignkey')
    
    # Remove columns from tournaments table
    op.drop_column('tournaments', 'schedule_generated')
    op.drop_column('tournaments', 'assigned_court_ids')
    op.drop_column('tournaments', 'hourly_time_slots')
    op.drop_column('tournaments', 'auto_schedule_enabled')
    op.drop_column('tournaments', 'recurring_tournament_id')
    
    # Drop tables
    op.drop_index(op.f('ix_tournament_participants_user_id'), table_name='tournament_participants')
    op.drop_index(op.f('ix_tournament_participants_tournament_id'), table_name='tournament_participants')
    op.drop_table('tournament_participants')
    
    op.drop_index(op.f('ix_recurring_tournament_category_templates_recurring_tournament_id'), table_name='recurring_tournament_category_templates')
    op.drop_table('recurring_tournament_category_templates')
    
    op.drop_index(op.f('ix_recurring_tournaments_id'), table_name='recurring_tournaments')
    op.drop_index(op.f('ix_recurring_tournaments_club_id'), table_name='recurring_tournaments')
    op.drop_table('recurring_tournaments')
    
    # Drop enum
    sa.Enum(name='recurrencepattern').drop(op.get_bind(), checkfirst=True)