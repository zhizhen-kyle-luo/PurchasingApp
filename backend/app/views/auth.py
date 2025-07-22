"""
Authentication routes
"""
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user, logout_user

from ..services import AuthService
from ..models import User

auth_bp = Blueprint('auth', __name__)
auth_service = AuthService()


@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400
    
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    remember = data.get('remember', False)
    
    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and password are required'}), 400
    
    # Authenticate user
    user = auth_service.authenticate_user(email, password)
    
    if not user:
        return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
    
    # Login user
    if auth_service.login_user_session(user, remember):
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': user.to_dict()
        })
    else:
        return jsonify({'success': False, 'message': 'Login failed'}), 500


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """User logout endpoint"""
    if auth_service.logout_user_session():
        return jsonify({'success': True, 'message': 'Logout successful'})
    else:
        return jsonify({'success': False, 'message': 'Logout failed'}), 500


@auth_bp.route('/register', methods=['POST'])
def register():
    """User registration endpoint"""
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400
    
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    full_name = data.get('full_name', '').strip()
    
    if not all([email, password, full_name]):
        return jsonify({'success': False, 'message': 'All fields are required'}), 400
    
    # Register user
    result = auth_service.register_user(email, password, full_name)
    
    if result['success']:
        return jsonify({
            'success': True,
            'message': result['message'],
            'user': result['user'].to_dict() if result['user'] else None
        }), 201
    else:
        return jsonify({'success': False, 'message': result['message']}), 400


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Initiate password reset"""
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400
    
    email = data.get('email', '').strip().lower()
    
    if not email:
        return jsonify({'success': False, 'message': 'Email is required'}), 400
    
    result = auth_service.initiate_password_reset(email)
    
    return jsonify({
        'success': result['success'],
        'message': result['message']
    })


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password with token"""
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400
    
    token = data.get('token', '')
    new_password = data.get('password', '')
    
    if not token or not new_password:
        return jsonify({'success': False, 'message': 'Token and password are required'}), 400
    
    result = auth_service.reset_password(token, new_password)
    
    if result['success']:
        return jsonify({'success': True, 'message': result['message']})
    else:
        return jsonify({'success': False, 'message': result['message']}), 400


@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """Get current user information"""
    return jsonify({
        'success': True,
        'user': current_user.to_dict()
    })


@auth_bp.route('/me', methods=['PUT'])
@login_required
def update_profile():
    """Update user profile"""
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400
    
    full_name = data.get('full_name', '').strip()
    
    result = auth_service.update_user_profile(current_user, full_name)
    
    if result['success']:
        return jsonify({
            'success': True,
            'message': result['message'],
            'user': current_user.to_dict()
        })
    else:
        return jsonify({'success': False, 'message': result['message']}), 400


@auth_bp.route('/check-permissions', methods=['POST'])
@login_required
def check_permissions():
    """Check user permissions"""
    data = request.get_json()
    
    required_role = data.get('role') if data else None
    required_permissions = data.get('permissions', []) if data else []
    
    has_permissions = auth_service.check_user_permissions(
        current_user, 
        required_role, 
        required_permissions
    )
    
    return jsonify({
        'success': True,
        'has_permissions': has_permissions,
        'user_permissions': auth_service.get_user_permissions(current_user)
    })
