"""Phase 1 enhancements - Add onboarding, team persistence, and position tracking

Revision ID: 7a1b2c3d4e5f
Revises: final_tournament_fixes
Create Date: 2025-07-10 12:00:00.000000

"""
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7a1b2c3d4e5f"
down_revision: Union[str, None] = "final_tournament_fixes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema for Phase 1 enhancements."""
    
    # Check if columns exist before adding them to handle cases where models
    # are already updated but migrations haven't been run
    connection = op.get_bind()
    
    # 1. Add onboarding tracking to users table (if not exists)
    # Check if onboarding_completed column exists
    result = connection.execute(sa.text("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'onboarding_completed'
    """))
    if not result.fetchone():
        op.add_column("users", sa.Column("onboarding_completed", sa.Boolean(), nullable=False, server_default="false"))
    
    # Check if onboarding_completed_at column exists
    result = connection.execute(sa.text("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'onboarding_completed_at'
    """))
    if not result.fetchone():
        op.add_column("users", sa.Column("onboarding_completed_at", sa.DateTime(), nullable=True))
    
    # 2. Extend teams table for persistence (if not exists)
    # Check if description column exists
    result = connection.execute(sa.text("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'teams' AND column_name = 'description'
    """))
    if not result.fetchone():
        op.add_column("teams", sa.Column("description", sa.Text(), nullable=True))
    
    # Check if logo_url column exists
    result = connection.execute(sa.text("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'teams' AND column_name = 'logo_url'
    """))
    if not result.fetchone():
        op.add_column("teams", sa.Column("logo_url", sa.Text(), nullable=True))
    
    # Check if created_by column exists
    result = connection.execute(sa.text("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'teams' AND column_name = 'created_by'
    """))
    if not result.fetchone():
        op.add_column("teams", sa.Column("created_by", sa.Integer(), nullable=True))
        # Add foreign key constraint for created_by
        op.create_foreign_key(
            "fk_teams_created_by_users",
            "teams",
            "users",
            ["created_by"],
            ["id"]
        )
    
    # Check if created_at column exists
    result = connection.execute(sa.text("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'teams' AND column_name = 'created_at'
    """))
    if not result.fetchone():
        op.add_column("teams", sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")))
    
    # Check if is_active column exists
    result = connection.execute(sa.text("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'teams' AND column_name = 'is_active'
    """))
    if not result.fetchone():
        op.add_column("teams", sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"))
    
    # 3. Create team_memberships table (if not exists)
    result = connection.execute(sa.text("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_name = 'team_memberships'
    """))
    if not result.fetchone():
        # Create required enums first
        connection.execute(sa.text("""
            DO $$ BEGIN
                CREATE TYPE teammembershiprole AS ENUM ('OWNER', 'ADMIN', 'MEMBER');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """))
        
        connection.execute(sa.text("""
            DO $$ BEGIN
                CREATE TYPE teammembershipstatus AS ENUM ('ACTIVE', 'INACTIVE', 'PENDING', 'REMOVED');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """))
        
        op.create_table(
            "team_memberships",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("team_id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("role", sa.Enum("OWNER", "ADMIN", "MEMBER", name="teammembershiprole"), nullable=False, server_default="MEMBER"),
            sa.Column("status", sa.Enum("ACTIVE", "INACTIVE", "PENDING", "REMOVED", name="teammembershipstatus"), nullable=False, server_default="ACTIVE"),
            sa.Column("joined_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("left_at", sa.DateTime(), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
            sa.ForeignKeyConstraint(["team_id"], ["teams.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("team_id", "user_id", name="uq_team_memberships_team_user")
        )
        
        # Create indexes for team_memberships
        op.create_index(op.f("ix_team_memberships_id"), "team_memberships", ["id"], unique=False)
        op.create_index(op.f("ix_team_memberships_team_id"), "team_memberships", ["team_id"], unique=False)
        op.create_index(op.f("ix_team_memberships_user_id"), "team_memberships", ["user_id"], unique=False)
    
    # 4. Add position tracking to game_players (if not exists)
    # Check if position column exists
    result = connection.execute(sa.text("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'game_players' AND column_name = 'position'
    """))
    if not result.fetchone():
        # Create the enum first
        connection.execute(sa.text("""
            DO $$ BEGIN
                CREATE TYPE gameplayerposition AS ENUM ('LEFT', 'RIGHT');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """))
        op.add_column("game_players", sa.Column("position", sa.Enum("LEFT", "RIGHT", name="gameplayerposition"), nullable=True))
    
    # Check if team_side column exists
    result = connection.execute(sa.text("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'game_players' AND column_name = 'team_side'
    """))
    if not result.fetchone():
        # Create the enum first
        connection.execute(sa.text("""
            DO $$ BEGIN
                CREATE TYPE gameplayerteamside AS ENUM ('TEAM_1', 'TEAM_2');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """))
        op.add_column("game_players", sa.Column("team_side", sa.Enum("TEAM_1", "TEAM_2", name="gameplayerteamside"), nullable=True))


def downgrade() -> None:
    """Downgrade schema for Phase 1 enhancements."""
    
    # Get connection for checking if items exist
    connection = op.get_bind()
    
    # Remove position tracking from game_players (if exists)
    try:
        result = connection.execute(sa.text("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'game_players' AND column_name = 'team_side'
        """))
        if result.fetchone():
            op.drop_column("game_players", "team_side")
            connection.execute(sa.text("DROP TYPE IF EXISTS gameplayerteamside"))
    except Exception:
        pass
    
    try:
        result = connection.execute(sa.text("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'game_players' AND column_name = 'position'
        """))
        if result.fetchone():
            op.drop_column("game_players", "position")
            connection.execute(sa.text("DROP TYPE IF EXISTS gameplayerposition"))
    except Exception:
        pass
    
    # Drop team_memberships table (if exists)
    try:
        result = connection.execute(sa.text("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_name = 'team_memberships'
        """))
        if result.fetchone():
            op.drop_index(op.f("ix_team_memberships_user_id"), table_name="team_memberships")
            op.drop_index(op.f("ix_team_memberships_team_id"), table_name="team_memberships")
            op.drop_index(op.f("ix_team_memberships_id"), table_name="team_memberships")
            op.drop_table("team_memberships")
            connection.execute(sa.text("DROP TYPE IF EXISTS teammembershiprole"))
            connection.execute(sa.text("DROP TYPE IF EXISTS teammembershipstatus"))
    except Exception:
        pass
    
    # Remove team persistence extensions (if exists)
    try:
        result = connection.execute(sa.text("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'teams' AND column_name = 'created_by'
        """))
        if result.fetchone():
            op.drop_constraint("fk_teams_created_by_users", "teams", type_="foreignkey")
            op.drop_column("teams", "created_by")
    except Exception:
        pass
    
    try:
        result = connection.execute(sa.text("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'teams' AND column_name = 'is_active'
        """))
        if result.fetchone():
            op.drop_column("teams", "is_active")
    except Exception:
        pass
        
    try:
        result = connection.execute(sa.text("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'teams' AND column_name = 'created_at'
        """))
        if result.fetchone():
            op.drop_column("teams", "created_at")
    except Exception:
        pass
        
    try:
        result = connection.execute(sa.text("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'teams' AND column_name = 'logo_url'
        """))
        if result.fetchone():
            op.drop_column("teams", "logo_url")
    except Exception:
        pass
        
    try:
        result = connection.execute(sa.text("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'teams' AND column_name = 'description'
        """))
        if result.fetchone():
            op.drop_column("teams", "description")
    except Exception:
        pass
    
    # Remove onboarding tracking from users (if exists)
    try:
        result = connection.execute(sa.text("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'onboarding_completed_at'
        """))
        if result.fetchone():
            op.drop_column("users", "onboarding_completed_at")
    except Exception:
        pass
        
    try:
        result = connection.execute(sa.text("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'onboarding_completed'
        """))
        if result.fetchone():
            op.drop_column("users", "onboarding_completed")
    except Exception:
        pass