from flask import Blueprint, session, redirect, url_for, request, jsonify, current_app
from .auth import auth
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')

@auth_bp.route('/login')
def login():
    if not auth.is_enabled():
        return jsonify({'error': 'Authentication not configured'}), 400
        
    redirect_uri = url_for('auth_bp.callback', _external=True, _scheme='https')
    return auth.keycloak.authorize_redirect(redirect_uri)

@auth_bp.route('/callback')
def callback():
    if not auth.is_enabled():
        return jsonify({'error': 'Authentication not configured'}), 400
        
    try:
        token = auth.keycloak.authorize_access_token()
        user_info = token.get('userinfo')
        
        if user_info:
            session['user'] = {
                'id': user_info.get('sub'),
                'email': user_info.get('email'),
                'name': user_info.get('name', user_info.get('preferred_username')),
                'username': user_info.get('preferred_username')
            }
            session['token'] = token
            logger.info(f"User logged in: {session['user']['email']}")
            
        return redirect('/')
        
    except Exception as e:
        logger.error(f"Authentication callback error: {str(e)}")
        return redirect('/?auth_error=1')

@auth_bp.route('/logout')
def logout():
    if not auth.is_enabled():
        return redirect('/')
        
    user = session.get('user')
    if user:
        logger.info(f"User logged out: {user.get('email')}")
        
    session.clear()
    
    # Keycloak logout URL
    server_url = current_app.config.get('KEYCLOAK_SERVER_URL')
    realm = current_app.config.get('KEYCLOAK_REALM')
    
    if server_url and realm:
        logout_url = f"{server_url}/realms/{realm}/protocol/openid-connect/logout"
        redirect_uri = url_for('index_alt', _external=True, _scheme='https')
        return redirect(f"{logout_url}?redirect_uri={redirect_uri}")
    
    return redirect('/')

@auth_bp.route('/user')
def user_info():
    if not auth.is_enabled():
        return jsonify({'authenticated': False, 'auth_enabled': False})
        
    user = auth.get_user_info()
    if user:
        return jsonify({
            'authenticated': True,
            'auth_enabled': True,
            'user': user
        })
    else:
        return jsonify({'authenticated': False, 'auth_enabled': True})
