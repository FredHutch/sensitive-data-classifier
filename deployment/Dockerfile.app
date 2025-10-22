# syntax=docker/dockerfile:1

FROM python:3.11-slim AS base
WORKDIR /app

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MODEL_CACHE_DIR=/app/models_cache

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for models and uploads
RUN mkdir -p /app/models_cache /app/uploads && \
    chmod 755 /app/models_cache /app/uploads

# Expose port
EXPOSE 5000

# Use Gunicorn for production
CMD ["gunicorn", "-c", "deployment/gunicorn.conf.py", "app:create_app()"]
