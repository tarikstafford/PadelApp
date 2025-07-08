"""Final tournament fixes - ensure all existing data is properly initialized

Revision ID: final_tournament_fixes
Revises: fix_existing_tournaments_data
Create Date: 2025-01-07 17:15:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'final_tournament_fixes'
down_revision = 'fix_existing_tournaments_data'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Get connection for data operations
    connection = op.get_bind()
    
    # Ensure all tournament fields have proper defaults
    # This handles any tournaments that might still have NULL values
    
    # Set defaults for all nullable fields
    connection.execute(sa.text("""
        UPDATE tournaments 
        SET description = '' 
        WHERE description IS NULL;
    """))
    
    connection.execute(sa.text("""
        UPDATE tournaments 
        SET entry_fee = 0.0 
        WHERE entry_fee IS NULL;
    """))
    
    connection.execute(sa.text("""
        UPDATE tournaments 
        SET auto_schedule_enabled = FALSE 
        WHERE auto_schedule_enabled IS NULL;
    """))
    
    connection.execute(sa.text("""
        UPDATE tournaments 
        SET schedule_generated = FALSE 
        WHERE schedule_generated IS NULL;
    """))
    
    connection.execute(sa.text("""
        UPDATE tournaments 
        SET hourly_time_slots = '[]'::jsonb 
        WHERE hourly_time_slots IS NULL;
    """))
    
    connection.execute(sa.text("""
        UPDATE tournaments 
        SET assigned_court_ids = '[]'::jsonb 
        WHERE assigned_court_ids IS NULL;
    """))
    
    # Make sure created_at and updated_at are set
    connection.execute(sa.text("""
        UPDATE tournaments 
        SET created_at = NOW() 
        WHERE created_at IS NULL;
    """))
    
    connection.execute(sa.text("""
        UPDATE tournaments 
        SET updated_at = NOW() 
        WHERE updated_at IS NULL;
    """))
    
    # Ensure all category configs have proper elo ranges
    connection.execute(sa.text("""
        UPDATE tournament_category_configs 
        SET min_elo = 1.0, max_elo = 2.0 
        WHERE category = 'BRONZE' AND (min_elo IS NULL OR max_elo IS NULL);
    """))
    
    connection.execute(sa.text("""
        UPDATE tournament_category_configs 
        SET min_elo = 2.0, max_elo = 3.0 
        WHERE category = 'SILVER' AND (min_elo IS NULL OR max_elo IS NULL);
    """))
    
    connection.execute(sa.text("""
        UPDATE tournament_category_configs 
        SET min_elo = 3.0, max_elo = 5.0 
        WHERE category = 'GOLD' AND (min_elo IS NULL OR max_elo IS NULL);
    """))
    
    connection.execute(sa.text("""
        UPDATE tournament_category_configs 
        SET min_elo = 5.0, max_elo = 10.0 
        WHERE category = 'PLATINUM' AND (min_elo IS NULL OR max_elo IS NULL);
    """))


def downgrade() -> None:
    # No downgrade needed for data fixes
    pass