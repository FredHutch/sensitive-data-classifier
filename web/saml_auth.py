"""
SAML Authentication Module

Provides Single Sign-On (SSO) authentication via SAML 2.0
Supports identity providers like:
- Microsoft Entra ID (Azure AD)
- Okta
- OneLogin
- Auth0
- Any SAML 2.0 compliant IdP
"""

import os
import logging
from functools import wraps
from flask import Blueprint, request, redirect, session, url_for, make_response, jsonify
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.utils import OneLogin_Saml2_Utils

logger = logging.getLogger(__name__)

saml_bp = Blueprint('saml', __name__, url_prefix='/saml')

def init_saml_auth(req):
    """Initialize SAML authentication object with settings."""
    auth = OneLogin_Saml2_Auth(req, custom_base_path=get_saml_settings_path())
    return auth

def get_saml_settings_path():
    """Get path to SAML settings directory."""
    saml_path = os.environ.get('SAML_SETTINGS_PATH', '/app/config/saml')
    if not os.path.exists(saml_path):
        logger.warning(f"SAML settings path does not exist: {saml_path}")
        os.makedirs(saml_path, exist_ok=True)
    return saml_path

def prepare_flask_request(request):
    """Prepare Flask request object for python3-saml."""
    url_data = request.url.split('?')
    return {
        'https': 'on' if request.scheme == 'https' else 'off',
        'http_host': request.host,
        'server_port': request.environ.get('SERVER_PORT', '443' if request.scheme == 'https' else '80'),
        'script_name': request.path,
        'get_data': request.args.copy(),
        'post_data': request.form.copy(),
        'query_string': url_data[1] if len(url_data) > 1 else ''
    }

def saml_required(f):
    """
    Decorator to require SAML authentication for routes.

    Usage:
        @app.route('/protected')
        @saml_required
        def protected_route():
            return f"Hello {session['saml_user_email']}"
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if SAML is enabled
        if not os.environ.get('SAML_ENABLED', 'false').lower() == 'true':
            # SAML not enabled, check for API key or allow access
            return f(*args, **kwargs)

        # Check if user is authenticated via SAML
        if 'saml_authenticated' not in session or not session['saml_authenticated']:
            # Store the original URL to redirect back after login
            session['saml_relay_state'] = request.url
            return redirect(url_for('saml.login'))

        return f(*args, **kwargs)
    return decorated_function

@saml_bp.route('/metadata')
def metadata():
    """
    SAML metadata endpoint.
    Provides SP (Service Provider) metadata to IdP for configuration.
    """
    try:
        req = prepare_flask_request(request)
        auth = init_saml_auth(req)
        settings = auth.get_settings()
        metadata = settings.get_sp_metadata()
        errors = settings.validate_metadata(metadata)

        if len(errors) == 0:
            resp = make_response(metadata, 200)
            resp.headers['Content-Type'] = 'text/xml'
            return resp
        else:
            logger.error(f"SAML metadata validation errors: {errors}")
            return jsonify({'error': 'Error generating metadata', 'details': errors}), 500
    except Exception as e:
        logger.error(f"Error generating SAML metadata: {str(e)}")
        return jsonify({'error': 'Error generating metadata', 'details': str(e)}), 500

@saml_bp.route('/login')
def login():
    """
    Initiate SAML login.
    Redirects user to IdP login page.
    """
    try:
        req = prepare_flask_request(request)
        auth = init_saml_auth(req)

        # Get relay state (return URL after login)
        relay_state = session.get('saml_relay_state', url_for('web.index', _external=True))

        # Redirect to IdP for authentication
        sso_url = auth.login(return_to=relay_state)
        return redirect(sso_url)
    except Exception as e:
        logger.error(f"Error initiating SAML login: {str(e)}")
        return jsonify({'error': 'SAML login failed', 'details': str(e)}), 500

@saml_bp.route('/acs', methods=['POST'])
def acs():
    """
    Assertion Consumer Service (ACS) endpoint.
    Receives SAML response from IdP after authentication.
    """
    try:
        req = prepare_flask_request(request)
        auth = init_saml_auth(req)
        auth.process_response()

        errors = auth.get_errors()

        if len(errors) == 0:
            # Authentication successful
            if auth.is_authenticated():
                # Store user information in session
                session['saml_authenticated'] = True
                session['saml_nameid'] = auth.get_nameid()
                session['saml_session_index'] = auth.get_session_index()

                # Get user attributes from SAML response
                attributes = auth.get_attributes()
                session['saml_user_email'] = attributes.get('http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress',
                                                           attributes.get('email', ['']))[0]
                session['saml_user_name'] = attributes.get('http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name',
                                                          attributes.get('name', ['']))[0]
                session['saml_user_groups'] = attributes.get('http://schemas.microsoft.com/ws/2008/06/identity/claims/groups',
                                                            attributes.get('groups', []))

                logger.info(f"SAML login successful for user: {session['saml_user_email']}")

                # Redirect to relay state or homepage
                relay_state = request.form.get('RelayState')
                if relay_state:
                    return redirect(OneLogin_Saml2_Utils.get_self_url(req) + relay_state)
                else:
                    return redirect(url_for('web.index'))
            else:
                logger.error("SAML authentication failed: User not authenticated")
                return jsonify({'error': 'Authentication failed'}), 401
        else:
            logger.error(f"SAML errors: {errors}")
            logger.error(f"SAML last error reason: {auth.get_last_error_reason()}")
            return jsonify({'error': 'SAML authentication error', 'details': errors}), 401
    except Exception as e:
        logger.error(f"Error processing SAML response: {str(e)}")
        return jsonify({'error': 'Error processing SAML response', 'details': str(e)}), 500

@saml_bp.route('/sls')
def sls():
    """
    Single Logout Service (SLS) endpoint.
    Handles logout requests from IdP.
    """
    try:
        req = prepare_flask_request(request)
        auth = init_saml_auth(req)

        url = auth.process_slo(delete_session_cb=lambda: session.clear())
        errors = auth.get_errors()

        if len(errors) == 0:
            if url is not None:
                return redirect(url)
            else:
                return redirect(url_for('web.index'))
        else:
            logger.error(f"SAML SLS errors: {errors}")
            return jsonify({'error': 'SLS error', 'details': errors}), 500
    except Exception as e:
        logger.error(f"Error processing SAML SLS: {str(e)}")
        return jsonify({'error': 'Error processing logout', 'details': str(e)}), 500

@saml_bp.route('/logout')
def logout():
    """
    Initiate SAML logout.
    Redirects user to IdP logout page.
    """
    try:
        req = prepare_flask_request(request)
        auth = init_saml_auth(req)

        # Get NameID and SessionIndex for logout
        name_id = session.get('saml_nameid')
        session_index = session.get('saml_session_index')

        # Clear local session
        session.clear()

        # Redirect to IdP for logout
        if name_id:
            return redirect(auth.logout(name_id=name_id, session_index=session_index))
        else:
            return redirect(url_for('web.index'))
    except Exception as e:
        logger.error(f"Error initiating SAML logout: {str(e)}")
        session.clear()
        return redirect(url_for('web.index'))

@saml_bp.route('/status')
def status():
    """
    Check SAML authentication status.
    Returns user information if authenticated.
    """
    if session.get('saml_authenticated'):
        return jsonify({
            'authenticated': True,
            'email': session.get('saml_user_email'),
            'name': session.get('saml_user_name'),
            'groups': session.get('saml_user_groups', [])
        })
    else:
        return jsonify({'authenticated': False})

def create_saml_config_template():
    """
    Create template SAML configuration files.
    Call this during initialization if config files don't exist.
    """
    saml_path = get_saml_settings_path()

    # Create settings.json template
    settings_file = os.path.join(saml_path, 'settings.json')
    if not os.path.exists(settings_file):
        settings_template = '''{
    "strict": true,
    "debug": false,
    "sp": {
        "entityId": "https://your-domain.com/saml/metadata",
        "assertionConsumerService": {
            "url": "https://your-domain.com/saml/acs",
            "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
        },
        "singleLogoutService": {
            "url": "https://your-domain.com/saml/sls",
            "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
        },
        "NameIDFormat": "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress",
        "x509cert": "",
        "privateKey": ""
    },
    "idp": {
        "entityId": "https://sts.windows.net/YOUR-TENANT-ID/",
        "singleSignOnService": {
            "url": "https://login.microsoftonline.com/YOUR-TENANT-ID/saml2",
            "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
        },
        "singleLogoutService": {
            "url": "https://login.microsoftonline.com/YOUR-TENANT-ID/saml2",
            "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
        },
        "x509cert": "YOUR-IDP-CERTIFICATE-HERE"
    },
    "security": {
        "nameIdEncrypted": false,
        "authnRequestsSigned": false,
        "logoutRequestSigned": false,
        "logoutResponseSigned": false,
        "signMetadata": false,
        "wantMessagesSigned": false,
        "wantAssertionsSigned": false,
        "wantAssertionsEncrypted": false,
        "wantNameIdEncrypted": false,
        "requestedAuthnContext": true,
        "signatureAlgorithm": "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256",
        "digestAlgorithm": "http://www.w3.org/2001/04/xmlenc#sha256"
    }
}'''
        with open(settings_file, 'w') as f:
            f.write(settings_template)
        logger.info(f"Created SAML settings template at {settings_file}")

    # Create advanced_settings.json template
    advanced_file = os.path.join(saml_path, 'advanced_settings.json')
    if not os.path.exists(advanced_file):
        advanced_template = '''{
    "security": {
        "authnRequestsSigned": false,
        "wantAssertionsSigned": true
    },
    "contactPerson": {
        "technical": {
            "givenName": "Technical Contact",
            "emailAddress": "technical@your-domain.com"
        },
        "support": {
            "givenName": "Support Contact",
            "emailAddress": "support@your-domain.com"
        }
    },
    "organization": {
        "en-US": {
            "name": "Your Organization",
            "displayname": "Your Organization Display Name",
            "url": "https://your-domain.com"
        }
    }
}'''
        with open(advanced_file, 'w') as f:
            f.write(advanced_template)
        logger.info(f"Created SAML advanced settings template at {advanced_file}")

# Initialize SAML config on module import if enabled
if os.environ.get('SAML_ENABLED', 'false').lower() == 'true':
    create_saml_config_template()
