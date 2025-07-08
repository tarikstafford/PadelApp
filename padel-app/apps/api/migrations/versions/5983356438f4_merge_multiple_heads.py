"""merge_multiple_heads

Revision ID: 5983356438f4
Revises: e8e8874a165c, 1e186f44b91d
Create Date: 2025-07-08 11:56:50.465511

"""
from collections.abc import Sequence
from typing import Union

# revision identifiers, used by Alembic.
revision: str = "5983356438f4"
down_revision: Union[str, None] = ("e8e8874a165c", "1e186f44b91d")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""


def downgrade() -> None:
    """Downgrade schema."""
