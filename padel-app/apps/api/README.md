# PadelGo API Backend

This directory contains the FastAPI backend for the PadelGo application.

## Setup

1.  Navigate to this directory (`padel-app/apps/api`).
2.  Create a Python virtual environment: `python -m venv .venv`
3.  Activate the virtual environment: `source .venv/bin/activate` (on macOS/Linux) or `.venv\Scripts\activate` (on Windows).
4.  Install dependencies: `pip install -e .`
5.  Set up your `.env` file with the `DATABASE_URL` and any other required environment variables (see `app/core/config.py`).

## Running the Development Server

```bash
# From within padel-app/apps/api/ and with virtual environment activated:
cd ../.. # Go to monorepo root (padel-app)
pnpm --filter api dev
```
Or, directly using uvicorn (from `padel-app/apps/api/` with venv activated):
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Database Migrations (Alembic)

Ensure your `DATABASE_URL` is correctly set in your environment.

1.  **Generate a new migration (after model changes):**
    ```bash
    # From padel-app/apps/api/ with virtual environment activated
    alembic revision -m "Your descriptive migration message" --autogenerate
    ```
2.  **Apply migrations:**
    ```bash
    alembic upgrade head
    ```

## Database Seeding

To populate the database with initial sample data (clubs, courts, etc.):

1.  Ensure the database schema is up-to-date (run Alembic migrations if needed).
2.  Make sure your `DATABASE_URL` is correctly configured in your environment.
3.  Run the seeding script from the `padel-app/apps/api/` directory (with your virtual environment activated):
    ```bash
    python app/seeds/run_seeds.py
    ```

This script is designed to be idempotent (it won't create duplicate data if run multiple times). 