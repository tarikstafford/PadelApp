"""comprehensive_game_management_enhancements

Revision ID: d5c986b34c46
Revises: 5983356438f4
Create Date: 2025-07-10 14:46:01.339357

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'd5c986b34c46'
down_revision: Union[str, None] = '5983356438f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema with comprehensive game management enhancements."""
    
    # Use raw SQL with proper error handling for PostgreSQL
    connection = op.get_bind()
    
    # 1. Add columns to users table
    connection.execute(sa.text("""
        DO $$ 
        BEGIN
            -- Add onboarding_completed if it doesn't exist
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name='users' AND column_name='onboarding_completed') THEN
                ALTER TABLE users ADD COLUMN onboarding_completed BOOLEAN NOT NULL DEFAULT FALSE;
            END IF;
            
            -- Add onboarding_completed_at if it doesn't exist
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name='users' AND column_name='onboarding_completed_at') THEN
                ALTER TABLE users ADD COLUMN onboarding_completed_at TIMESTAMP WITH TIME ZONE;
            END IF;
            
            -- Add is_game_history_public if it doesn't exist
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name='users' AND column_name='is_game_history_public') THEN
                ALTER TABLE users ADD COLUMN is_game_history_public BOOLEAN NOT NULL DEFAULT TRUE;
            END IF;
            
            -- Add is_game_statistics_public if it doesn't exist
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name='users' AND column_name='is_game_statistics_public') THEN
                ALTER TABLE users ADD COLUMN is_game_statistics_public BOOLEAN NOT NULL DEFAULT TRUE;
            END IF;
        END $$;
    """))
    
    # 2. Add columns to teams table
    connection.execute(sa.text("""
        DO $$ 
        BEGIN
            -- Add description if it doesn't exist
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name='teams' AND column_name='description') THEN
                ALTER TABLE teams ADD COLUMN description TEXT;
            END IF;
            
            -- Add logo_url if it doesn't exist
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name='teams' AND column_name='logo_url') THEN
                ALTER TABLE teams ADD COLUMN logo_url VARCHAR;
            END IF;
            
            -- Add created_by if it doesn't exist
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name='teams' AND column_name='created_by') THEN
                ALTER TABLE teams ADD COLUMN created_by INTEGER REFERENCES users(id);
            END IF;
            
            -- Add created_at if it doesn't exist
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name='teams' AND column_name='created_at') THEN
                ALTER TABLE teams ADD COLUMN created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP;
            END IF;
            
            -- Add is_active if it doesn't exist
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name='teams' AND column_name='is_active') THEN
                ALTER TABLE teams ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE;
            END IF;
        END $$;
    """))
    
    # 3. Create ENUMs if they don't exist
    connection.execute(sa.text("""
        DO $$ 
        BEGIN
            -- Create teammembershiprole enum
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'teammembershiprole') THEN
                CREATE TYPE teammembershiprole AS ENUM ('OWNER', 'ADMIN', 'MEMBER');
            END IF;
            
            -- Create teammembershipstatus enum
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'teammembershipstatus') THEN
                CREATE TYPE teammembershipstatus AS ENUM ('ACTIVE', 'INACTIVE', 'PENDING', 'REMOVED');
            END IF;
            
            -- Create gameplayerposition enum
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'gameplayerposition') THEN
                CREATE TYPE gameplayerposition AS ENUM ('LEFT', 'RIGHT');
            END IF;
            
            -- Create gameplayerteamside enum
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'gameplayerteamside') THEN
                CREATE TYPE gameplayerteamside AS ENUM ('TEAM_1', 'TEAM_2');
            END IF;
        END $$;
    """))
    
    # 4. Create team_memberships table if it doesn't exist
    connection.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS team_memberships (
            id SERIAL PRIMARY KEY,
            team_id INTEGER NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            role teammembershiprole NOT NULL DEFAULT 'MEMBER',
            status teammembershipstatus NOT NULL DEFAULT 'ACTIVE',
            joined_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
            left_at TIMESTAMP WITH TIME ZONE,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            CONSTRAINT unique_team_user_membership UNIQUE (team_id, user_id)
        );
    """))
    
    # 5. Create indexes if they don't exist
    connection.execute(sa.text("""
        CREATE INDEX IF NOT EXISTS idx_team_memberships_team_id ON team_memberships(team_id);
        CREATE INDEX IF NOT EXISTS idx_team_memberships_user_id ON team_memberships(user_id);
        CREATE INDEX IF NOT EXISTS idx_team_memberships_active ON team_memberships(team_id, is_active);
    """))
    
    # 6. Add columns to game_players table
    connection.execute(sa.text("""
        DO $$ 
        BEGIN
            -- Add position if it doesn't exist
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name='game_players' AND column_name='position') THEN
                ALTER TABLE game_players ADD COLUMN position gameplayerposition;
            END IF;
            
            -- Add team_side if it doesn't exist
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name='game_players' AND column_name='team_side') THEN
                ALTER TABLE game_players ADD COLUMN team_side gameplayerteamside;
            END IF;
        END $$;
    """))


def downgrade() -> None:
    """Downgrade schema - remove comprehensive game management enhancements."""
    
    connection = op.get_bind()
    
    # Drop columns from game_players
    connection.execute(sa.text("""
        ALTER TABLE game_players DROP COLUMN IF EXISTS team_side;
        ALTER TABLE game_players DROP COLUMN IF EXISTS position;
    """))
    
    # Drop team_memberships table
    connection.execute(sa.text("DROP TABLE IF EXISTS team_memberships;"))
    
    # Drop columns from teams
    connection.execute(sa.text("""
        ALTER TABLE teams DROP COLUMN IF EXISTS is_active;
        ALTER TABLE teams DROP COLUMN IF EXISTS created_at;
        ALTER TABLE teams DROP COLUMN IF EXISTS created_by;
        ALTER TABLE teams DROP COLUMN IF EXISTS logo_url;
        ALTER TABLE teams DROP COLUMN IF EXISTS description;
    """))
    
    # Drop columns from users
    connection.execute(sa.text("""
        ALTER TABLE users DROP COLUMN IF EXISTS is_game_statistics_public;
        ALTER TABLE users DROP COLUMN IF EXISTS is_game_history_public;
        ALTER TABLE users DROP COLUMN IF EXISTS onboarding_completed_at;
        ALTER TABLE users DROP COLUMN IF EXISTS onboarding_completed;
    """))
    
    # Drop enums
    connection.execute(sa.text("""
        DROP TYPE IF EXISTS gameplayerteamside;
        DROP TYPE IF EXISTS gameplayerposition;
        DROP TYPE IF EXISTS teammembershipstatus;
        DROP TYPE IF EXISTS teammembershiprole;
    """))