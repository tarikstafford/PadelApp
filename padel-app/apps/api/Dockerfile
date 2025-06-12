# Cache-busting comment to force a redeploy: 2025-06-11 12:30
# Stage 1: Build the Python environment
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Copy all necessary configuration files, scripts, and directories
# from their specific locations within the monorepo context.
COPY apps/api/pyproject.toml ./
COPY apps/api/alembic.ini ./
COPY apps/api/entrypoint.sh ./
COPY apps/api/migrations ./migrations

RUN chmod +x ./entrypoint.sh

# Install dependencies
RUN pip install --no-cache-dir -U pip setuptools wheel
RUN pip install --no-cache-dir .

# Copy the application code
COPY apps/api/app ./app

# Create static directories
RUN mkdir -p app/static/profile_pics
RUN mkdir -p app/static/club_pics

# Expose the port the app runs on
EXPOSE 8000

# Set the entrypoint
ENTRYPOINT ["./entrypoint.sh"]

# Default command to pass to the entrypoint script
# Using shell form to allow environment variable substitution for ${PORT}
CMD gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:${PORT:-8000} 