#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

# Run database migrations
# Ensure alembic is callable. If installed in a venv inside the container that isn't on PATH by default,
# you might need to specify the path to alembic or activate the venv.
# However, with `pip install .` in Dockerfile, it should be in the PATH.
echo "Running database migrations..."
alembic upgrade head
echo "Database migrations complete."

# Execute the main command (passed as arguments to this script)
# This will be our gunicorn command specified in the Dockerfile CMD or passed to the entrypoint.
echo "Starting application server..."
exec "$@" 