#!/usr/bin/env python3
"""
PHI Classifier & Synthetic Data Generator
Main Application Entry Point (Blueprint-wired)

Author: Generated for FredHutch
Date: October 2025
Version: 1.0.0
"""

import logging
from flask import Flask

# Web blueprint (HTML pages + REST API)
from web import web_bp

# Core services (ensure these imports match your project structure)
from core.processor import DocumentProcessor
from core.classifier import AdvancedPHIClassifier
from core.generator import SyntheticHealthDataGenerator

logger = logging.getLogger(__name__)


def create_app() -> Flask:
    """Flask application factory that wires services and registers the web blueprint."""
    app = Flask(__name__)

    # Wire application services consumed by routes
    app.config["APP_SERVICES"] = {
        "processor": DocumentProcessor(),
        "classifier": AdvancedPHIClassifier(),
        "generator": SyntheticHealthDataGenerator(),
    }

    # Register web blueprint
    app.register_blueprint(web_bp)

    # Simple health endpoint (redundant with web.routes /health, but cheap)
    @app.get("/health")
    def health():
        return {"status": "healthy"}

    logger.info("Application created and services wired successfully")
    return app


# Enable `python app.py` for local development; use gunicorn in production
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=False)
