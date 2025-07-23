"""
User model and related enums
"""
from enum import Enum
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import secrets

from .base import db, BaseModel


class UserRole(Enum):
    """User role enumeration"""
    REQUESTER = 'requester'
    SUBLEAD = 'sublead'
    EXECUTIVE = 'executive'
    BUSINESS = 'business'
    
    @classmethod
    def get_choices(cls):
        """Get choices for forms"""
        return [(role.value, role.value.title()) for role in cls]


class User(UserMixin, BaseModel):
    """User model for authentication and authorization"""
    __tablename__ = 'users'
    
    # Basic info
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)  # Increased from 120
    password_hash = db.Column(db.String(255), nullable=False)  # Increased from 200
    full_name = db.Column(db.String(255), nullable=False)  # Increased from 120
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.REQUESTER)
    
    # Account status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    email_verified = db.Column(db.Boolean, default=False, nullable=False)
    
    # Password reset
    reset_token = db.Column(db.String(255), unique=True)  # Increased from 100
    reset_token_expiry = db.Column(db.DateTime)
    
    # Last login tracking
    last_login = db.Column(db.DateTime)
    login_count = db.Column(db.Integer, default=0)
    
    # Relationships
    purchases = db.relationship('Purchase', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def set_password(self, password: str) -> None:
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Check password against hash"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def generate_reset_token(self) -> str:
        """Generate password reset token"""
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
        db.session.commit()
        return self.reset_token
    
    def verify_reset_token(self, token: str) -> bool:
        """Verify password reset token"""
        if not self.reset_token or not self.reset_token_expiry:
            return False
        
        if self.reset_token != token:
            return False
            
        if datetime.utcnow() > self.reset_token_expiry:
            return False
            
        return True
    
    def clear_reset_token(self) -> None:
        """Clear password reset token"""
        self.reset_token = None
        self.reset_token_expiry = None
        db.session.commit()
    
    def record_login(self) -> None:
        """Record user login"""
        self.last_login = datetime.utcnow()
        self.login_count += 1
        db.session.commit()
    
    # Role checking methods
    def is_requester(self) -> bool:
        """Check if user is a requester"""
        return self.role == UserRole.REQUESTER
    
    def is_sublead(self) -> bool:
        """Check if user is a sublead"""
        return self.role == UserRole.SUBLEAD
    
    def is_executive(self) -> bool:
        """Check if user is an executive"""
        return self.role == UserRole.EXECUTIVE
    
    def is_business(self) -> bool:
        """Check if user is business team"""
        return self.role == UserRole.BUSINESS
    
    def can_approve_orders(self) -> bool:
        """Check if user can approve orders"""
        return self.role in [UserRole.SUBLEAD, UserRole.EXECUTIVE]
    
    def can_manage_orders(self) -> bool:
        """Check if user can manage order fulfillment"""
        return self.role == UserRole.BUSINESS
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        data = super().to_dict()
        data.update({
            'role': self.role.value if self.role else None,
            'is_active': self.is_active,
            'email_verified': self.email_verified,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'login_count': self.login_count
        })
        # Remove sensitive fields
        data.pop('password_hash', None)
        data.pop('reset_token', None)
        data.pop('reset_token_expiry', None)
        return data
    
    @staticmethod
    def get_approved_emails():
        """Get list of approved email addresses"""
        # This could be moved to a separate configuration or database table
        return {
            'requester': [
                'requester@mit.edu',
            ],
            'sublead': [
                'sublead@mit.edu',
            ],
            'executive': [
                'executive@mit.edu',
            ],
            'business': [
                'business@mit.edu',
            ]
        }