import logging
import os
import sys

# Adjust the Python path to include the main 'app' directory
# This allows us to import modules like app.database, app.models, etc.
# Assumes run_seeds.py is in app/seeds/ and the main app package is one level up.
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.abspath(
    os.path.join(current_dir, "..")
)  # Points to the 'app' directory
project_root_api = os.path.abspath(os.path.join(app_dir, ".."))  # Points to 'apps/api'

if app_dir not in sys.path:
    sys.path.insert(0, app_dir)
if project_root_api not in sys.path:
    sys.path.insert(
        0, project_root_api
    )  # To find app.module if app is not directly in PYTHONPATH


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    logger.info("Initializing database session for seeding...")
    try:
        # These imports are here to ensure sys.path is set first
        from app.database import SessionLocal  # noqa: PLC0415
        from app.seeds.seed_data import seed_all_data  # noqa: PLC0415

        # Optional: Create tables if they don't exist.
        # This is usually handled by Alembic migrations in a production setup.
        # For a simple seeding script, you might want to ensure tables are there.
        # logger.info("Creating database tables if they don't exist (via Base.metadata.create_all)...")
        # Base.metadata.create_all(bind=engine) # Be cautious with this in a migration-managed DB

        db = SessionLocal()
        try:
            seed_all_data(db)
        finally:
            db.close()
            logger.info("Database session closed.")
    except ImportError as e:
        logger.exception(f"Error importing application modules: {e}")
        logger.exception(
            "Please ensure that the script is run from the correct directory or PYTHONPATH is set."
        )
    except Exception as e:
        logger.exception(f"An error occurred during the seeding process: {e}")


if __name__ == "__main__":
    main()
