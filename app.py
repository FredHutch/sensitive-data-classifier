#!/usr/bin/env python3
"""
PHI Classifier & Synthetic Data Generator
Main Application Entry Point

A secure, HIPAA-compliant Python web application for automated detection
of Protected Health Information (PHI) in documents and generation of
synthetic health data for testing and development purposes.

Author: Generated for FredHutch
Date: October 2025
Version: 1.0.0
"""

import os
import sys
import logging
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify, render_template, send_file
from werkzeug.utils import secure_filename
from config.settings import Config
from core.security import SecurityManager
from core.classifier import AdvancedPHIClassifier
from core.generator import SyntheticHealthDataGenerator
from web.routes import setup_routes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('phi_classifier.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class PHIClassifierApp:
    """
    Main PHI Classifier Application
    
    Integrates all components: security, classification, data generation,
    and web interface into a single deployable application.
    """
    
    def __init__(self, config_name='default'):
        """
        Initialize the PHI Classifier application
        
        Args:
            config_name (str): Configuration environment name
        """
        self.config = Config()
        self.app = Flask(__name__)
        self.app.config.from_object(self.config)
        
        # Initialize core components
        self.security_manager = SecurityManager()
        self.classifier = AdvancedPHIClassifier()
        self.data_generator = SyntheticHealthDataGenerator()
        
        # Configure security
        self._configure_security()
        
        # Set up routes
        setup_routes(self.app, self)
        
        logger.info("PHI Classifier Application initialized successfully")
    
    def _configure_security(self):
        """
        Configure Flask security headers and settings
        """
        self.app.config['MAX_CONTENT_LENGTH'] = self.config.MAX_FILE_SIZE
        
        @self.app.after_request
        def add_security_headers(response):
            """
            Add security headers to all responses
            """
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            response.headers['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'"
            )
            return response
    
    def run(self, host='127.0.0.1', port=5000, debug=False):
        """
        Run the Flask application
        
        Args:
            host (str): Host address to bind to
            port (int): Port number to bind to
            debug (bool): Enable debug mode
        """
        logger.info(f"Starting PHI Classifier on {host}:{port}")
        
        # Use SSL in production
        ssl_context = None
        if not debug and self.config.ENABLE_SSL:
            ssl_context = 'adhoc'
        
        self.app.run(
            host=host,
            port=port,
            debug=debug,
            ssl_context=ssl_context,
            threaded=True
        )

def create_app(config_name='default'):
    """
    Application factory pattern
    
    Args:
        config_name (str): Configuration environment name
        
    Returns:
        Flask: Configured Flask application
    """
    phi_app = PHIClassifierApp(config_name)
    return phi_app.app

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='PHI Classifier & Synthetic Data Generator')
    parser.add_argument('--host', default='127.0.0.1', help='Host address (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=5000, help='Port number (default: 5000)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--config', default='default', help='Configuration name')
    
    args = parser.parse_args()
    
    # Create and run the application
    app_instance = PHIClassifierApp(args.config)
    app_instance.run(host=args.host, port=args.port, debug=args.debug)
