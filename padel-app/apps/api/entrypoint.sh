#!/bin/sh

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

# Now, run database migrations. Alembic will pick up the .env file via config.py.
echo "Running database migrations..."
alembic upgrade head
echo "Database migrations complete."

# Execute the main command (passed as arguments to this script)
echo "Starting application server..."
exec "$@" 