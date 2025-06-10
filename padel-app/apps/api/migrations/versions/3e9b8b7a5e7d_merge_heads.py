"""Merge heads

Revision ID: 3e9b8b7a5e7d
Revises: 2f5a4351b8c8, 860b6482a629
Create Date: 2025-06-08 06:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3e9b8b7a5e7d'
down_revision: Union[str, None] = ('2f5a4351b8c8', '860b6482a629')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass 