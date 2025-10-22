"""
API Authentication Module

Provides API key authentication for REST endpoints
"""

import logging
from functools import wraps
from flask import request, jsonify, current_app

logger = logging.getLogger(__name__)


def require_api_key(f):
    """
    Decorator to require API key authentication for endpoints

    Usage:
        @app.route('/api/endpoint')
        @require_api_key
        def endpoint():
            ...

    API key should be provided in header: X-API-Key

    Returns 401 if:
    - API_KEY_REQUIRED is True and no key provided
    - API_KEY_REQUIRED is True and key doesn't match
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if API key is required
        api_key_required = current_app.config.get('API_KEY_REQUIRED', False)

        if not api_key_required:
            # API key not required, proceed
            return f(*args, **kwargs)

        # Get API key from header
        provided_key = request.headers.get('X-API-Key')

        if not provided_key:
            logger.warning(f"API request to {request.path} rejected: No API key provided")
            return jsonify({
                'error': 'Authentication required',
                'message': 'Please provide API key in X-API-Key header'
            }), 401

        # Validate API key
        expected_key = current_app.config.get('API_KEY')

        if provided_key != expected_key:
            logger.warning(f"API request to {request.path} rejected: Invalid API key")
            return jsonify({
                'error': 'Authentication failed',
                'message': 'Invalid API key'
            }), 401

        # API key valid, proceed
        logger.debug(f"API request to {request.path} authenticated successfully")
        return f(*args, **kwargs)

    return decorated_function


def optional_api_key(f):
    """
    Decorator for endpoints that work with or without authentication,
    but may provide enhanced features when authenticated

    Returns user info in kwargs if authenticated
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        authenticated = False
        provided_key = request.headers.get('X-API-Key')
        expected_key = current_app.config.get('API_KEY')

        if provided_key and provided_key == expected_key:
            authenticated = True

        kwargs['authenticated'] = authenticated
        return f(*args, **kwargs)

    return decorated_function
