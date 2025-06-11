#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Run database migrations
echo "Running database migrations..."
# Add error handling to ensure migration command succeeds
if ! alembic upgrade head; then
    echo "Database migration failed. See logs for details."
    exit 1
fi
echo "Database migrations complete."

# Start the application
exec "$@" 