"""add_game_invitations_table

Revision ID: 451e8eef6b37
Revises: 627120000tsafe
Create Date: 2025-07-03 13:15:42.409062

"""
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "451e8eef6b37"
down_revision: Union[str, None] = "627120000tsafe"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create game_invitations table
    op.create_table("game_invitations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("game_id", sa.Integer(), nullable=False),
        sa.Column("token", sa.String(), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("max_uses", sa.Integer(), nullable=True),
        sa.Column("current_uses", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ),
        sa.ForeignKeyConstraint(["game_id"], ["games.id"], ),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index(op.f("ix_game_invitations_id"), "game_invitations", ["id"], unique=False)
    op.create_index(op.f("ix_game_invitations_token"), "game_invitations", ["token"], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_game_invitations_token"), table_name="game_invitations")
    op.drop_index(op.f("ix_game_invitations_id"), table_name="game_invitations")
    op.drop_table("game_invitations")
