-- Tournament System Migration Cleanup Script
-- Run this if you need to clean up a partially failed migration

-- Drop tournament tables if they exist (in reverse dependency order)
DROP TABLE IF EXISTS tournament_trophies CASCADE;
DROP TABLE IF EXISTS tournament_court_bookings CASCADE;
DROP TABLE IF EXISTS tournament_matches CASCADE;
DROP TABLE IF EXISTS tournament_teams CASCADE;
DROP TABLE IF EXISTS tournament_category_configs CASCADE;
DROP TABLE IF EXISTS tournaments CASCADE;

-- Drop enum types if they exist
DROP TYPE IF EXISTS matchstatus CASCADE;
DROP TYPE IF EXISTS tournamentcategory CASCADE;
DROP TYPE IF EXISTS tournamenttype CASCADE;
DROP TYPE IF EXISTS tournamentstatus CASCADE;

-- Optional: Remove the migration record if it was partially applied
-- DELETE FROM alembic_version WHERE version_num = '20250627_111615_add_tournament_system';

-- Show current alembic version
SELECT version_num FROM alembic_version;