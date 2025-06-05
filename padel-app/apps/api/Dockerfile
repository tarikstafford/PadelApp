# Base image
FROM python:3.11-slim

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Copy dependency definition files
COPY pyproject.toml ./

# Install dependencies
RUN pip install --no-cache-dir -U pip setuptools wheel
RUN pip install --no-cache-dir "." # This installs from pyproject.toml including gunicorn & alembic

# Copy the application code into the container
COPY ./app ./app

# Copy the entrypoint script and make it executable
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Expose the port the app runs on
EXPOSE 8000

# Set the entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command to pass to the entrypoint script (Gunicorn command)
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "--bind", "0.0.0.0:${PORT:-8000}"] 