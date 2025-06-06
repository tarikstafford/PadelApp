#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

echo "Running database migrations..."
alembic upgrade head
echo "Database migrations complete."

echo "Starting application server..."
exec "$@" 