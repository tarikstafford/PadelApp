"""add tournament participant model

Revision ID: add_tournament_participant
Revises: tournament_hourly_scheduling
Create Date: 2025-01-07 10:00:00.000000

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "add_tournament_participant"
down_revision = "tournament_hourly_scheduling"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create tournament_participants table
    op.create_table("tournament_participants",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tournament_id", sa.Integer(), nullable=False),
        sa.Column("category_config_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("seed", sa.Integer(), nullable=True),
        sa.Column("elo_rating", sa.Float(), nullable=False),
        sa.Column("registration_date", sa.DateTime(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("match_teams", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["category_config_id"], ["tournament_category_configs.id"], ),
        sa.ForeignKeyConstraint(["tournament_id"], ["tournaments.id"], ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index(op.f("ix_tournament_participants_id"), "tournament_participants", ["id"], unique=False)

    # Create unique constraint to prevent duplicate registrations
    op.create_unique_constraint(
        "uq_tournament_participants_user_tournament",
        "tournament_participants",
        ["tournament_id", "user_id"]
    )

    # Create indexes for better query performance
    op.create_index("ix_tournament_participants_tournament_id", "tournament_participants", ["tournament_id"])
    op.create_index("ix_tournament_participants_category_config_id", "tournament_participants", ["category_config_id"])
    op.create_index("ix_tournament_participants_user_id", "tournament_participants", ["user_id"])


def downgrade() -> None:
    # Drop indexes
    op.drop_index("ix_tournament_participants_user_id", table_name="tournament_participants")
    op.drop_index("ix_tournament_participants_category_config_id", table_name="tournament_participants")
    op.drop_index("ix_tournament_participants_tournament_id", table_name="tournament_participants")

    # Drop unique constraint
    op.drop_constraint("uq_tournament_participants_user_tournament", "tournament_participants", type_="unique")

    # Drop table
    op.drop_index(op.f("ix_tournament_participants_id"), table_name="tournament_participants")
    op.drop_table("tournament_participants")
