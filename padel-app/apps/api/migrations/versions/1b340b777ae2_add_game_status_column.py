"""add_game_status_column

Revision ID: 1b340b777ae2
Revises: 451e8eef6b37
Create Date: 2025-07-03 14:27:53.744307

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1b340b777ae2'
down_revision: Union[str, None] = '451e8eef6b37'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create the game status enum type
    connection = op.get_bind()
    connection.execute(sa.text("""
        DO $$ BEGIN
            CREATE TYPE gamestatus AS ENUM ('SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', 'EXPIRED');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """))
    
    # Add the game_status column with default value
    op.add_column('games', sa.Column('game_status', sa.Enum('SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', 'EXPIRED', name='gamestatus'), nullable=False, server_default='SCHEDULED'))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove the column
    op.drop_column('games', 'game_status')
    
    # Drop the enum type
    connection = op.get_bind()
    connection.execute(sa.text("DROP TYPE IF EXISTS gamestatus"))
