#!/usr/bin/env python3
"""
PHI Classifier & Synthetic Data Generator
Main Application Entry Point - Production Ready

Author: Generated for FredHutch
Date: October 2025
Version: 2.0.0

Features:
- Pre-trained ML models for PHI detection
- API authentication and rate limiting
- Production-ready deployment with Gunicorn
- Environment-based configuration
"""

import logging
from flask import Flask
from pathlib import Path

# Configuration
from config.app_config import Config

# Web blueprint (HTML pages + REST API)
from web import web_bp

# Core services
from core.processor import DocumentProcessor
from core.classifier import AdvancedPHIClassifier
from core.generator import SyntheticHealthDataGenerator

logger = logging.getLogger(__name__)


def create_app() -> Flask:
    """
    Flask application factory that wires services and registers the web blueprint.

    Returns:
        Flask: Configured Flask application instance
    """
    # Initialize Flask app
    app = Flask(__name__)

    # Load configuration
    config = Config.init_app()
    app.config.from_object(config)

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger.info(f"Starting PHI Classifier v2.0.0 in {config.ENVIRONMENT} mode")

    # Initialize services (with error handling)
    try:
        logger.info("Initializing document processor...")
        processor = DocumentProcessor()

        logger.info("Initializing PHI classifier with pre-trained models...")
        logger.info("Note: First run will download models (~500MB-1GB). This may take several minutes.")
        classifier = AdvancedPHIClassifier(cache_dir=str(config.MODEL_CACHE_DIR))

        # Validate classifier setup
        validation = classifier.validate_setup()
        if not validation['operational']:
            logger.error(f"Classifier validation failed: {validation['issues']}")
        if validation['warnings']:
            for warning in validation['warnings']:
                logger.warning(warning)

        logger.info("Initializing synthetic data generator...")
        generator = SyntheticHealthDataGenerator()

        # Wire application services
        app.config["APP_SERVICES"] = {
            "processor": processor,
            "classifier": classifier,
            "generator": generator,
        }

        logger.info("All services initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize services: {e}", exc_info=True)
        raise

    # Register web blueprint
    app.register_blueprint(web_bp)

    # Health check endpoint
    @app.get("/health")
    def health():
        """Health check endpoint for load balancers"""
        classifier = app.config["APP_SERVICES"]["classifier"]
        model_info = classifier.get_model_info()

        return {
            "status": "healthy",
            "version": "2.0.0",
            "environment": config.ENVIRONMENT,
            "models_loaded": model_info['models_available']
        }

    # Model information endpoint
    @app.get("/api/models/info")
    def model_info():
        """Get information about loaded ML models"""
        classifier = app.config["APP_SERVICES"]["classifier"]
        return classifier.get_model_info()

    logger.info("Application created and services wired successfully")
    logger.info(f"API authentication: {'enabled' if config.API_KEY_REQUIRED else 'disabled'}")
    logger.info(f"Rate limiting: {'enabled' if config.RATELIMIT_ENABLED else 'disabled'}")

    return app


# Enable `python app.py` for local development; use gunicorn in production
if __name__ == "__main__":
    import sys

    # Check if running in production
    if Config.ENVIRONMENT == "production":
        logger.error("ERROR: Do not run with 'python app.py' in production!")
        logger.error("Use Gunicorn instead: gunicorn -c deployment/gunicorn.conf.py 'app:create_app()'")
        sys.exit(1)

    logging.basicConfig(level=logging.DEBUG)
    logger.info("Running in development mode with Flask's built-in server")
    logger.info("For production, use Gunicorn")

    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
