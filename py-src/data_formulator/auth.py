import os
import secrets
from functools import wraps
from flask import session, request, redirect, url_for, jsonify, current_app
from authlib.integrations.flask_client import OAuth
from authlib.common.errors import AuthlibBaseError
import logging

logger = logging.getLogger(__name__)

class KeycloakAuth:
    def __init__(self, app=None):
        self.oauth = OAuth()
        self.keycloak = None
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        # Keycloak configuration
        keycloak_enabled = app.config.get('KEYCLOAK_ENABLED', False)
        
        if not keycloak_enabled:
            logger.info("Keycloak authentication is disabled")
            return
            
        server_url = app.config.get('KEYCLOAK_SERVER_URL')
        realm = app.config.get('KEYCLOAK_REALM')
        client_id = app.config.get('KEYCLOAK_CLIENT_ID')
        client_secret = app.config.get('KEYCLOAK_CLIENT_SECRET')
        
        if not all([server_url, realm, client_id, client_secret]):
            logger.warning("Keycloak configuration incomplete, authentication disabled")
            return
            
        # Configure OAuth
        self.oauth.init_app(app)
        
        # Register Keycloak provider
        self.keycloak = self.oauth.register(
            name='keycloak',
            client_id=client_id,
            client_secret=client_secret,
            server_metadata_url=f'{server_url}/realms/{realm}/.well-known/openid-configuration',
            client_kwargs={
                'scope': 'openid email profile'
            }
        )
        
        logger.info(f"Keycloak authentication configured for realm: {realm}")
    
    def is_enabled(self):
        return self.keycloak is not None
    
    def login_required(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not self.is_enabled():
                return f(*args, **kwargs)
                
            if 'user' not in session:
                return redirect(url_for('auth_bp.login'))
            return f(*args, **kwargs)
        return decorated_function
    
    def get_user_info(self):
        if not self.is_enabled() or 'user' not in session:
            return None
        return session['user']

# Global auth instance
auth = KeycloakAuth()