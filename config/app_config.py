"""
Simplified Application Configuration for PHI Classifier

Production-ready configuration with sensible defaults
"""

import os
from pathlib import Path

class Config:
    """
    Main application configuration

    Environment variables:
    - ENVIRONMENT: development|production|testing (default: development)
    - SECRET_KEY: Flask secret key (required in production)
    - API_KEY: API authentication key (required if API_KEY_REQUIRED=true)
    - MODEL_CACHE_DIR: Directory for caching ML models (default: ./models_cache)
    """

    # Environment
    ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")
    DEBUG = ENVIRONMENT == "development"

    # Security
    SECRET_KEY = os.environ.get("SECRET_KEY")
    API_KEY_REQUIRED = os.environ.get("API_KEY_REQUIRED", "false").lower() == "true"
    API_KEY = os.environ.get("API_KEY")

    # Application paths
    BASE_DIR = Path(__file__).parent.parent
    UPLOAD_FOLDER = Path(os.environ.get("UPLOAD_FOLDER", BASE_DIR / "uploads"))
    MODEL_CACHE_DIR = Path(os.environ.get("MODEL_CACHE_DIR", BASE_DIR / "models_cache"))

    # File handling
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'csv', 'xlsx', 'json'}

    # Rate limiting (requires redis)
    RATELIMIT_ENABLED = os.environ.get("RATELIMIT_ENABLED", "false").lower() == "true"
    RATELIMIT_STORAGE_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")

    # Logging
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO" if not DEBUG else "DEBUG")

    # CORS
    CORS_ENABLED = os.environ.get("CORS_ENABLED", "false").lower() == "true"

    @classmethod
    def init_app(cls):
        """Initialize application directories and validate config"""
        # Create directories
        cls.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
        cls.MODEL_CACHE_DIR.mkdir(parents=True, exist_ok=True)

        # Validate production config
        if cls.ENVIRONMENT == "production":
            if not cls.SECRET_KEY:
                raise ValueError("SECRET_KEY must be set in production!")
            if cls.API_KEY_REQUIRED and not cls.API_KEY:
                raise ValueError("API_KEY must be set when API_KEY_REQUIRED=true!")

        return cls
