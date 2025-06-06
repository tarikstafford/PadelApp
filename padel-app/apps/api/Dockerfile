# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy dependency definition and entrypoint script from their specific location
# within the monorepo context
COPY apps/api/pyproject.toml ./
COPY apps/api/entrypoint.sh ./
RUN chmod +x ./entrypoint.sh

# Install dependencies
RUN pip install --no-cache-dir -U pip setuptools wheel
RUN pip install --no-cache-dir .

# Copy the application code from its specific location
COPY apps/api/app ./app

# Expose the port the app runs on
EXPOSE 8000

# Set the entrypoint script
ENTRYPOINT ["./entrypoint.sh"]

# Default command to pass to the entrypoint script
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "--bind", "0.0.0.0:${PORT:-8000}"] 