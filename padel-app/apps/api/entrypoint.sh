#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Create a .env file from the environment variables provided by Railway
echo "Creating .env file from environment variables..."
echo "DATABASE_URL=${DATABASE_URL}" >> .env
echo "SECRET_KEY=${SECRET_KEY}" >> .env
echo "ALGORITHM=${ALGORITHM:-HS256}" >> .env
echo "ACCESS_TOKEN_EXPIRE_MINUTES=${ACCESS_TOKEN_EXPIRE_MINUTES:-1440}" >> .env
echo "REFRESH_TOKEN_EXPIRE_MINUTES=${REFRESH_TOKEN_EXPIRE_MINUTES:-43200}" >> .env
echo ".env file created."

# Run database migrations with explicit error handling
echo "Running database migrations..."
if ! alembic upgrade head; then
    echo "!!! DATABASE MIGRATION FAILED !!!"
    exit 1
fi
echo "Database migrations complete."

# Now, execute the command passed to this script (e.g., uvicorn, gunicorn)
exec "$@" 