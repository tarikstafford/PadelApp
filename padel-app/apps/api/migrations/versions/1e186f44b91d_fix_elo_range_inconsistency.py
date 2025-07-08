"""Fix ELO range inconsistency - align all tournament category configs with CATEGORY_ELO_RANGES

Revision ID: 1e186f44b91d
Revises: final_tournament_fixes
Create Date: 2025-01-08 12:00:00.000000

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "1e186f44b91d"
down_revision = "final_tournament_fixes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Get connection for data operations
    connection = op.get_bind()

    # Fix ELO ranges for all tournament category configs to match CATEGORY_ELO_RANGES
    # This ensures all existing tournament categories use the correct ELO ranges

    # BRONZE: (1.0, 2.0)
    connection.execute(sa.text("""
        UPDATE tournament_category_configs
        SET min_elo = 1.0, max_elo = 2.0
        WHERE category = 'BRONZE' AND (min_elo != 1.0 OR max_elo != 2.0);
    """))

    # SILVER: (2.0, 3.0)
    connection.execute(sa.text("""
        UPDATE tournament_category_configs
        SET min_elo = 2.0, max_elo = 3.0
        WHERE category = 'SILVER' AND (min_elo != 2.0 OR max_elo != 3.0);
    """))

    # GOLD: (3.0, 5.0) - This is the key fix
    connection.execute(sa.text("""
        UPDATE tournament_category_configs
        SET min_elo = 3.0, max_elo = 5.0
        WHERE category = 'GOLD' AND (min_elo != 3.0 OR max_elo != 5.0);
    """))

    # PLATINUM: (5.0, 10.0) - Using 10.0 instead of infinity for database storage
    connection.execute(sa.text("""
        UPDATE tournament_category_configs
        SET min_elo = 5.0, max_elo = 10.0
        WHERE category = 'PLATINUM' AND (min_elo != 5.0 OR max_elo != 10.0);
    """))

    # Also fix recurring tournament category templates
    connection.execute(sa.text("""
        UPDATE recurring_tournament_category_templates
        SET min_elo = 1.0, max_elo = 2.0
        WHERE category = 'BRONZE' AND (min_elo != 1.0 OR max_elo != 2.0);
    """))

    connection.execute(sa.text("""
        UPDATE recurring_tournament_category_templates
        SET min_elo = 2.0, max_elo = 3.0
        WHERE category = 'SILVER' AND (min_elo != 2.0 OR max_elo != 3.0);
    """))

    connection.execute(sa.text("""
        UPDATE recurring_tournament_category_templates
        SET min_elo = 3.0, max_elo = 5.0
        WHERE category = 'GOLD' AND (min_elo != 3.0 OR max_elo != 5.0);
    """))

    connection.execute(sa.text("""
        UPDATE recurring_tournament_category_templates
        SET min_elo = 5.0, max_elo = 10.0
        WHERE category = 'PLATINUM' AND (min_elo != 5.0 OR max_elo != 10.0);
    """))


def downgrade() -> None:
    # No downgrade needed for data consistency fixes
    pass
