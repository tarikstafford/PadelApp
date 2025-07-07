"""Merge tournament enhancements with notification models

Revision ID: e8e8874a165c
Revises: abc123456789, add_tournament_enhancements
Create Date: 2025-07-07 16:32:17.427626

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e8e8874a165c'
down_revision: Union[str, None] = ('abc123456789', 'add_tournament_enhancements')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
