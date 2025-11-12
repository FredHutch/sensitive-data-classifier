# syntax=docker/dockerfile:1

FROM python:3.11-slim AS base
WORKDIR /app

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MODEL_CACHE_DIR=/app/models_cache

# Install system dependencies including OCR tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    libxml2-dev \
    libxmlsec1-dev \
    libxmlsec1-openssl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for models, uploads, and sessions
RUN mkdir -p /app/models_cache /app/uploads /app/flask_sessions /app/config/saml && \
    chmod 755 /app/models_cache /app/uploads /app/flask_sessions /app/config/saml

# Expose port
EXPOSE 5000

# Use Gunicorn for production
CMD ["gunicorn", "-c", "deployment/gunicorn.conf.py", "app:create_app()"]
