"""
Web Interface Package

Flask-based web interface for PHI classification and synthetic data generation.
Provides both HTML interface and REST API endpoints.
"""

__version__ = '1.0.0'
__author__ = 'FredHutch PHI Classifier Team'

from flask import Flask
from .routes import setup_routes

__all__ = ['setup_routes', 'create_app']

def create_app(config_name='default'):
    """
    Application factory for creating Flask app instances
    
    Args:
        config_name (str): Configuration environment name
        
    Returns:
        Flask: Configured Flask application
    """
    app = Flask(__name__)
    
    # Configure app
    app.config['SECRET_KEY'] = 'phi-classifier-secret-key-change-in-production'
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB
    
    # Set up routes
    setup_routes(app)
    
    return app