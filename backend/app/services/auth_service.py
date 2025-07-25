"""
Authentication and authorization service
"""
from typing import Optional, Dict, Any
from flask import current_app
from flask_login import login_user, logout_user

from ..models import User, UserRole
from ..models.base import db
from .email_service import EmailService


class AuthService:
    """Service for handling authentication and user management"""
    
    @staticmethod
    def authenticate_user(email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        if not email or not password:
            return None
        
        user = User.query.filter_by(email=email.lower().strip()).first()
        
        if user and user.check_password(password) and user.is_active:
            user.record_login()
            return user
        
        return None
    
    @staticmethod
    def login_user_session(user: User, remember: bool = False) -> bool:
        """Log user into session"""
        try:
            login_user(user, remember=remember)
            current_app.logger.info(f'User {user.email} logged in successfully')
            return True
        except Exception as e:
            current_app.logger.error(f'Login failed for user {user.email}: {str(e)}')
            return False
    
    @staticmethod
    def logout_user_session() -> bool:
        """Log user out of session"""
        try:
            logout_user()
            return True
        except Exception as e:
            current_app.logger.error(f'Logout failed: {str(e)}')
            return False
    
    @staticmethod
    def register_user(email: str, password: str, full_name: str, role: str = None) -> Dict[str, Any]:
        """Register a new user"""
        result = {'success': False, 'message': '', 'user': None}
        
        # Validate input
        if not email or not password or not full_name:
            result['message'] = 'All fields are required'
            return result
        
        email = email.lower().strip()
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            result['message'] = 'Email already registered'
            return result
        
        # Validate email against approved list
        approved_emails = User.get_approved_emails()
        user_role = None
        
        for role_name, emails in approved_emails.items():
            if email in emails:
                user_role = UserRole(role_name)
                break
        
        if not user_role:
            result['message'] = 'Email not in approved list'
            return result
        
        try:
            # Create new user
            user = User(
                email=email,
                full_name=full_name.strip(),
                role=user_role
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            result['success'] = True
            result['message'] = 'Registration successful'
            result['user'] = user
            
            current_app.logger.info(f'New user registered: {email} as {user_role.value}')
            
        except Exception as e:
            db.session.rollback()
            result['message'] = f'Registration failed: {str(e)}'
            current_app.logger.error(f'Registration failed for {email}: {str(e)}')
        
        return result
    
    @staticmethod
    def initiate_password_reset(email: str) -> Dict[str, Any]:
        """Initiate password reset process"""
        result = {'success': False, 'message': ''}
        
        if not email:
            result['message'] = 'Email is required'
            return result
        
        user = User.query.filter_by(email=email.lower().strip()).first()
        
        if not user:
            # Don't reveal if email exists or not for security
            result['success'] = True
            result['message'] = 'If the email exists, a reset link has been sent'
            return result
        
        try:
            # Generate reset token
            token = user.generate_reset_token()
            
            # Send reset email
            email_service = EmailService()
            email_sent = email_service.send_password_reset_email(user, token)
            
            if email_sent:
                result['success'] = True
                result['message'] = 'Password reset email sent'
                current_app.logger.info(f'Password reset initiated for {user.email}')
            else:
                result['message'] = 'Failed to send reset email'
                
        except Exception as e:
            result['message'] = 'Failed to initiate password reset'
            current_app.logger.error(f'Password reset failed for {email}: {str(e)}')
        
        return result
    
    @staticmethod
    def reset_password(token: str, new_password: str) -> Dict[str, Any]:
        """Reset password with token"""
        result = {'success': False, 'message': ''}
        
        if not token or not new_password:
            result['message'] = 'Token and new password are required'
            return result
        
        user = User.query.filter_by(reset_token=token).first()
        
        if not user or not user.verify_reset_token(token):
            result['message'] = 'Invalid or expired reset token'
            return result
        
        try:
            # Update password
            user.set_password(new_password)
            user.clear_reset_token()
            
            result['success'] = True
            result['message'] = 'Password reset successful'
            
            current_app.logger.info(f'Password reset completed for {user.email}')
            
        except Exception as e:
            result['message'] = 'Failed to reset password'
            current_app.logger.error(f'Password reset failed for user {user.email}: {str(e)}')
        
        return result
    
    @staticmethod
    def update_user_profile(user: User, full_name: str = None) -> Dict[str, Any]:
        """Update user profile information"""
        result = {'success': False, 'message': ''}
        
        try:
            if full_name:
                user.full_name = full_name.strip()
            
            db.session.commit()
            
            result['success'] = True
            result['message'] = 'Profile updated successfully'
            
        except Exception as e:
            db.session.rollback()
            result['message'] = f'Failed to update profile: {str(e)}'
            current_app.logger.error(f'Profile update failed for {user.email}: {str(e)}')
        
        return result
    
    @staticmethod
    def check_user_permissions(user: User, required_role: str = None, required_permissions: list = None) -> bool:
        """Check if user has required permissions"""
        if not user or not user.is_active:
            return False
        
        if required_role:
            if user.role.value != required_role:
                return False
        
        if required_permissions:
            user_permissions = AuthService.get_user_permissions(user)
            for permission in required_permissions:
                if permission not in user_permissions:
                    return False
        
        return True
    
    @staticmethod
    def get_user_permissions(user: User) -> list:
        """Get list of permissions for user based on role"""
        if not user:
            return []
        
        base_permissions = ['view_own_orders', 'create_orders']
        
        if user.is_sublead():
            return base_permissions + ['approve_orders', 'view_team_orders']
        elif user.is_executive():
            return base_permissions + ['approve_orders', 'view_all_orders', 'executive_approval']
        elif user.is_business():
            return base_permissions + ['manage_orders', 'view_all_orders', 'purchase_orders']
        else:
            return base_permissions
